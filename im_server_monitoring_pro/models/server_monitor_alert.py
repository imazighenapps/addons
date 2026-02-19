# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class ServerMonitorAlert(models.Model):
    _name = 'server.monitor.alert'
    _description = 'Server Monitoring Alerts'
    _order = 'create_date desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    config_id = fields.Many2one(
        'server.monitor.config',
        string='Configuration',
        required=True,
        ondelete='cascade'
    )
    history_id = fields.Many2one(
        'server.monitor.history',
        string='History Record',
        ondelete='set null'
    )

    metric_type = fields.Selection([
        ('cpu', 'CPU'),
        ('ram', 'RAM'),
        ('disk', 'Disk'),
        ('network', 'Network'),
        ('process', 'Process'),
    ], string='Metric', required=True, index=True)

    severity = fields.Selection([
        ('info', 'Information'),
        ('warning', 'Warning'),
        ('critical', 'Critical'),
    ], string='Severity', required=True, default='warning',
        tracking=True)

    state = fields.Selection([
        ('open', 'Open'),
        ('acknowledged', 'Acknowledged'),
        ('resolved', 'Resolved'),
    ], string='Status', default='open', required=True,
        tracking=True, index=True)

    value = fields.Float(string='Measured Value', digits=(10, 2))
    threshold = fields.Float(string='Exceeded Threshold', digits=(10, 2))
    message = fields.Text(string='Alert Message', required=True)

    acknowledged_by = fields.Many2one('res.users', string='Acknowledged By', readonly=True)
    acknowledged_date = fields.Datetime(string='Acknowledged On', readonly=True)
    resolved_date = fields.Datetime(string='Resolved On', readonly=True)
    notes = fields.Text(string='Notes')

    email_sent = fields.Boolean(string='Email Sent', default=False)

    severity_color = fields.Char(
        string='Color',
        compute='_compute_severity_color',
        store=False
    )

    @api.depends('severity')
    def _compute_severity_color(self):
        colors = {
            'info': '#17a2b8',
            'warning': '#ffc107',
            'critical': '#dc3545',
        }
        for rec in self:
            rec.severity_color = colors.get(rec.severity, '#6c757d')

    @api.model
    def create(self, vals):
        record = super().create(vals)
        record._send_notifications()
        return record

    def _send_notifications(self):
        """Send email and Odoo notifications"""
        self.ensure_one()
        config = self.config_id

        if self.severity not in ('warning', 'critical'):
            return

        # Odoo notification (chatter)
        if config.enable_odoo_notifications and config.alert_user_ids:
            severity_label = dict(self._fields['severity'].selection).get(self.severity, '')
            icon = '🔴' if self.severity == 'critical' else '🟡'
            subject = _(f"{icon} Server Alert - {severity_label} : {dict(self._fields['metric_type'].selection).get(self.metric_type, '')}")

            for user in config.alert_user_ids:
                self.env['mail.message'].create({
                    'message_type': 'notification',
                    'subject': subject,
                    'body': f"<p>{self.message}</p>",
                    'partner_ids': [(4, user.partner_id.id)],
                    'model': self._name,
                    'res_id': self.id,
                    'notification_ids': [(0, 0, {
                        'res_partner_id': user.partner_id.id,
                        'notification_type': 'inbox',
                    })],
                })

        # Email notification
        if config.enable_email_alerts and config.alert_email_ids and not self.email_sent:
            try:
                template_data = {
                    'subject': _(f"[Server Monitor] {self.severity.upper()} Alert - {self.metric_type.upper()}"),
                    'body_html': self._build_email_body(),
                    'email_to': ','.join(config.alert_email_ids.mapped('email')),
                }
                mail = self.env['mail.mail'].create(template_data)
                mail.send()
                self.write({'email_sent': True})
            except Exception as e:
                _logger.error(f"Error sending alert email: {e}")

    def _build_email_body(self):
        """Build alert email body"""
        severity_colors = {
            'warning': '#ffc107',
            'critical': '#dc3545',
            'info': '#17a2b8',
        }
        color = severity_colors.get(self.severity, '#6c757d')
        metric_label = dict(self._fields['metric_type'].selection).get(self.metric_type, self.metric_type)
        severity_label = dict(self._fields['severity'].selection).get(self.severity, self.severity)
        icon = '🔴' if self.severity == 'critical' else '🟡'

        return f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: {color}; color: white; padding: 20px; border-radius: 8px 8px 0 0;">
                <h2 style="margin: 0;">{icon} Server Alert - {severity_label}</h2>
            </div>
            <div style="background: #f8f9fa; padding: 20px; border: 1px solid #dee2e6;">
                <table style="width: 100%; border-collapse: collapse;">
                    <tr>
                        <td style="padding: 8px; font-weight: bold; width: 40%;">Metric:</td>
                        <td style="padding: 8px;">{metric_label}</td>
                    </tr>
                    <tr style="background: white;">
                        <td style="padding: 8px; font-weight: bold;">Measured Value:</td>
                        <td style="padding: 8px; color: {color}; font-weight: bold;">{self.value:.1f}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; font-weight: bold;">Threshold:</td>
                        <td style="padding: 8px;">{self.threshold:.1f}</td>
                    </tr>
                    <tr style="background: white;">
                        <td style="padding: 8px; font-weight: bold;">Message:</td>
                        <td style="padding: 8px;">{self.message}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; font-weight: bold;">Date:</td>
                        <td style="padding: 8px;">{self.create_date}</td>
                    </tr>
                </table>
                <div style="margin-top: 20px; padding: 10px; background: #fff3cd; border-radius: 4px;">
                    <strong>Action Required:</strong> Please check your server and acknowledge this alert in Odoo.
                </div>
            </div>
        </div>
        """

    def action_acknowledge(self):
        """Acknowledge the alert"""
        self.ensure_one()
        self.write({
            'state': 'acknowledged',
            'acknowledged_by': self.env.user.id,
            'acknowledged_date': fields.Datetime.now(),
        })
        self.message_post(
            body=_(f"Alert acknowledged by {self.env.user.name}"),
            message_type='notification'
        )

    def action_resolve(self):
        """Mark alert as resolved"""
        self.ensure_one()
        self.write({
            'state': 'resolved',
            'resolved_date': fields.Datetime.now(),
        })
        self.message_post(
            body=_(f"Alert resolved by {self.env.user.name}"),
            message_type='notification'
        )

    def action_acknowledge_all(self):
        """Acknowledge all open alerts"""
        open_alerts = self.search([('state', '=', 'open')])
        open_alerts.write({
            'state': 'acknowledged',
            'acknowledged_by': self.env.user.id,
            'acknowledged_date': fields.Datetime.now(),
        })
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Alerts Acknowledged'),
                'message': _(f'{len(open_alerts)} alert(s) acknowledged.'),
                'type': 'success',
            }
        }
