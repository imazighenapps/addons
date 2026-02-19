# -*- coding: utf-8 -*-
import psutil
import logging
import signal
from odoo import models, fields, api, _
from odoo.exceptions import UserError, AccessError

_logger = logging.getLogger(__name__)


class ServerMonitorKillWizard(models.TransientModel):
    _name = 'server.monitor.kill.wizard'
    _description = 'Process Termination Confirmation'

    pid = fields.Integer(string='PID', required=True)
    process_name = fields.Char(string='Process Name', required=True)
    process_user = fields.Char(string='Process User')
    cpu_percent = fields.Float(string='CPU (%)')
    memory_mb = fields.Float(string='Memory (MB)')
    force_kill = fields.Boolean(
        string='Force (SIGKILL)',
        default=False,
        help='Use SIGKILL if SIGTERM fails. Use with caution.'
    )
    confirmation = fields.Boolean(
        string='I confirm I want to kill this process',
        required=True,
        default=False
    )
    warning_message = fields.Text(
        string='Warning',
        compute='_compute_warning',
        store=False
    )

    @api.depends('process_name', 'pid')
    def _compute_warning(self):
        for rec in self:
            rec.warning_message = _(
                f"⚠️ WARNING: You are about to kill the process "
                f"'{rec.process_name}' (PID: {rec.pid}).\n\n"
                f"This action may affect the system. "
                f"Make sure you know what you are doing.\n\n"
                f"This action will be recorded in the audit logs."
            )

    def action_kill(self):
        """Execute process termination with confirmation"""
        self.ensure_one()

        if not self.env.user.has_group('im_server_monitoring_pro.group_server_monitor_admin'):
            raise AccessError(_("Only administrators can terminate processes."))

        if not self.confirmation:
            raise UserError(_("You must check the confirmation box before proceeding."))

        protected_names = [
            'systemd', 'init', 'kthreadd', 'odoo', 'python',
            'postgres', 'nginx', 'apache2', 'sshd', 'cron',
        ]
        if self.process_name.lower() in protected_names or self.pid <= 100:
            raise UserError(_(f"The process '{self.process_name}' is protected."))

        try:
            proc = psutil.Process(self.pid)

            if self.force_kill:
                proc.kill()  # SIGKILL
                signal_used = 'SIGKILL'
            else:
                proc.terminate()  # SIGTERM
                signal_used = 'SIGTERM'

            _logger.warning(
                f"[AUDIT] Process terminated ({signal_used}) by {self.env.user.name} "
                f"(ID: {self.env.user.id}): PID={self.pid}, Name={self.process_name}"
            )

            # Log in alerts
            config = self.env['server.monitor.config'].search([], limit=1)
            if config:
                self.env['server.monitor.alert'].create({
                    'config_id': config.id,
                    'metric_type': 'process',
                    'severity': 'info',
                    'value': self.pid,
                    'threshold': 0,
                    'message': _(
                        f"[AUDIT] Process terminated ({signal_used}) by {self.env.user.name}: "
                        f"PID={self.pid}, Name={self.process_name}, Signal={signal_used}"
                    ),
                    'state': 'resolved',
                })

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Process Terminated'),
                    'message': _(f"'{self.process_name}' (PID: {self.pid}) terminated with {signal_used}."),
                    'type': 'success',
                }
            }

        except psutil.NoSuchProcess:
            raise UserError(_(f"Process PID {self.pid} no longer exists."))
        except psutil.AccessDenied:
            raise UserError(_("Permission denied. The process requires root privileges."))
        except Exception as e:
            raise UserError(_(f"Error: {e}"))
