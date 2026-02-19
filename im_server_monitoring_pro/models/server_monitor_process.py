# -*- coding: utf-8 -*-
import logging
import psutil
import os
import signal
from odoo import models, fields, api, _
from odoo.exceptions import UserError, AccessError
from datetime import datetime

_logger = logging.getLogger(__name__)


class ServerMonitorProcess(models.Model):
    _name = 'server.monitor.process'
    _description = 'Server Process Management'
    _order = 'cpu_percent desc'
    _rec_name = 'name'

    # Process snapshot (non-persistent, refreshed on demand)
    pid = fields.Integer(string='PID', readonly=True)
    name = fields.Char(string='Process Name', readonly=True)
    username = fields.Char(string='User', readonly=True)
    status = fields.Char(string='Status', readonly=True)
    cpu_percent = fields.Float(string='CPU (%)', digits=(5, 2), readonly=True)
    memory_percent = fields.Float(string='Memory (%)', digits=(5, 2), readonly=True)
    memory_mb = fields.Float(string='Memory (MB)', digits=(10, 2), readonly=True)
    num_threads = fields.Integer(string='Threads', readonly=True)
    create_time = fields.Datetime(string='Started On', readonly=True)
    cmdline = fields.Text(string='Command Line', readonly=True)
    snapshot_date = fields.Datetime(string='Snapshot Taken On', readonly=True)

    is_system_process = fields.Boolean(
        string='System Process',
        compute='_compute_is_system',
        store=True
    )

    @api.depends('username')
    def _compute_is_system(self):
        system_users = ['root', 'daemon', 'www-data', 'postgres', 'nobody', 'sys', 'bin']
        for rec in self:
            rec.is_system_process = rec.username in system_users

    @api.model
    def refresh_processes(self):
        """Deletes old snapshots and creates a new process snapshot"""
        # Delete old snapshots (> 5 minutes)
        from datetime import datetime, timedelta
        cutoff = fields.Datetime.now() - timedelta(minutes=5)
        self.search([('snapshot_date', '<', cutoff)]).unlink()

        # Create a new snapshot
        processes = []
        now = fields.Datetime.now()

        for proc in psutil.process_iter([
            'pid', 'name', 'username', 'status',
            'cpu_percent', 'memory_percent', 'num_threads', 'create_time', 'cmdline'
        ]):
            try:
                pinfo = proc.info
                mem_info = proc.memory_info()

                create_time = pinfo.get('create_time')
                if create_time:
                    create_time_dt = datetime.fromtimestamp(create_time)
                else:
                    create_time_dt = now

                processes.append({
                    'pid': pinfo['pid'],
                    'name': pinfo['name'] or 'Unknown',
                    'username': pinfo['username'] or 'unknown',
                    'status': pinfo['status'] or 'unknown',
                    'cpu_percent': pinfo['cpu_percent'] or 0.0,
                    'memory_percent': pinfo['memory_percent'] or 0.0,
                    'memory_mb': mem_info.rss / 1024**2,
                    'num_threads': pinfo['num_threads'] or 0,
                    'create_time': create_time_dt,
                    'cmdline': ' '.join(pinfo['cmdline'] or [])[:500],
                    'snapshot_date': now,
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue

        # Sort by CPU
        processes.sort(key=lambda x: x['cpu_percent'], reverse=True)

        # Keep only the top 100 processes
        for proc_data in processes[:100]:
            try:
                from datetime import datetime
                if isinstance(proc_data.get('create_time'), float):
                    proc_data['create_time'] = datetime.fromtimestamp(proc_data['create_time'])
            except Exception:
                proc_data['create_time'] = now

            self.create(proc_data)

        return True

    def action_kill_process(self):
        """Kill a process (with security checks)"""
        self.ensure_one()

        # Permission check
        if not self.env.user.has_group('im_server_monitoring_pro.group_server_monitor_admin'):
            raise AccessError(_("Only administrators can terminate processes."))

        # Protected processes - never kill
        protected_names = [
            'systemd', 'init', 'kthreadd', 'odoo', 'python',
            'postgres', 'nginx', 'apache2', 'sshd', 'cron',
        ]
        if self.name.lower() in protected_names or self.pid <= 100:
            raise UserError(_(
                f"The process '{self.name}' (PID: {self.pid}) is protected and cannot be terminated."
            ))

        if self.is_system_process:
            raise UserError(_(
                f"System processes (user: {self.username}) cannot be terminated."
            ))

        try:
            proc = psutil.Process(self.pid)
            proc_name = proc.name()

            # Double-check the name
            if proc_name != self.name:
                raise UserError(_(
                    f"PID {self.pid} now belongs to '{proc_name}', not '{self.name}'. "
                    f"Refresh the list and try again."
                ))

            proc.terminate()  # SIGTERM first

            # Log the action
            _logger.warning(
                f"Process terminated by {self.env.user.name}: "
                f"PID={self.pid}, Name={self.name}, User={self.username}"
            )

            # Create an info alert
            config = self.env['server.monitor.config'].search([], limit=1)
            if config:
                self.env['server.monitor.alert'].create({
                    'config_id': config.id,
                    'metric_type': 'process',
                    'severity': 'info',
                    'value': self.pid,
                    'threshold': 0,
                    'message': _(
                        f"Process terminated by {self.env.user.name}: "
                        f"PID={self.pid}, Name={self.name}"
                    ),
                    'state': 'resolved',
                })

            # Delete the record
            self.unlink()

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Process Terminated'),
                    'message': _(f"The process '{proc_name}' (PID: {self.pid}) has been terminated."),
                    'type': 'success',
                }
            }
        except psutil.NoSuchProcess:
            raise UserError(_(f"Process PID {self.pid} no longer exists."))
        except psutil.AccessDenied:
            raise UserError(_(
                f"Permission denied to terminate process PID {self.pid}. "
                f"The Odoo server must have the required permissions."
            ))
        except Exception as e:
            raise UserError(_(f"Error while terminating the process: {e}"))

    @api.model
    def get_top_processes_data(self, limit=20):
        """Returns top process data for the dashboard"""
        processes = []
        for proc in psutil.process_iter([
            'pid', 'name', 'username', 'status',
            'cpu_percent', 'memory_percent'
        ]):
            try:
                pinfo = proc.info
                pinfo['memory_mb'] = proc.memory_info().rss / 1024**2
                processes.append(pinfo)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        processes.sort(key=lambda x: x.get('cpu_percent', 0), reverse=True)
        return processes[:limit]

    def action_server_monitor_kill_wizard(self):
        """Returns the kill wizard action with default values"""
        self.ensure_one()  # We work on a single process

        return {
            'name': _('Terminate Process'),
            'type': 'ir.actions.act_window',
            'res_model': 'server.monitor.kill.wizard',
            'view_mode': 'form',
            'target': 'new',
            'binding_model_id': self.env.ref('server_monitor.model_server_monitor_process').id,
            'binding_view_types': 'list,form',
            'context': {
                'default_pid': self.pid,
                'default_process_name': self.name,
                'default_process_user': self.username,
                'default_cpu_percent': self.cpu_percent,
                'default_memory_mb': self.memory_mb,
            },
        }
