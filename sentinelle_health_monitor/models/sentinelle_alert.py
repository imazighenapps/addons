# -*- coding: utf-8 -*-
# sentinelle_health_monitor/models/sentinelle_alert.py
"""
Alert model: represents a health problem that has been detected.
Alerts go through a lifecycle: open → acknowledged → resolved.
Notifications (email, Slack, Odoo channel) are dispatched here.
"""

import json
import logging
from datetime import timedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class SentinelleAlert(models.Model):
    """
    An alert is created when a metric exceeds its threshold.
    The cooldown mechanism prevents alert spam for the same issue.
    """
    _name = 'sentinelle.alert'
    _description = 'Sentinelle Health Alert'
    _order = 'create_date desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # ─── Identity ──────────────────────────────────────────────
    name = fields.Char(
        string='Alert Title',
        required=True,
        tracking=True,
    )
    alert_type = fields.Selection(
        selection=[
            ('orm_performance',  'ORM Performance'),
            ('sql_slow',         'Slow SQL Query'),
            ('sql_n_plus_one',   'N+1 SQL Detected'),
            ('api_slow',         'Slow External API'),
            ('api_failure',      'External API Failure'),
            ('log_errors',       'High Error Rate in Logs'),
            ('cron_delay',       'Cron Job Delayed'),
            ('cron_failure',     'Cron Job Failure'),
            ('sys_cpu',          'High CPU Usage'),
            ('sys_ram',          'High RAM Usage'),
            ('sys_disk',         'High Disk Usage'),
            ('custom',           'Custom Alert'),
        ],
        string='Alert Type',
        required=True,
        index=True,
    )
    severity = fields.Selection(
        selection=[
            ('info',     '🔵 Info'),
            ('warning',  '🟡 Warning'),
            ('critical', '🔴 Critical'),
        ],
        string='Severity',
        required=True,
        default='warning',
        index=True,
        tracking=True,
    )
    state = fields.Selection(
        selection=[
            ('open',         'Open'),
            ('acknowledged', 'Acknowledged'),
            ('resolved',     'Resolved'),
            ('muted',        'Muted'),
        ],
        string='Status',
        default='open',
        index=True,
        tracking=True,
    )

    # ─── Detail ────────────────────────────────────────────────
    description = fields.Text(
        string='Description',
        help='What was observed and why it triggered this alert.',
    )
    metric_id = fields.Many2one(
        'sentinelle.metric',
        string='Source Metric',
        ondelete='set null',
    )
    metric_value = fields.Float(string='Observed Value', digits=(16, 4))
    threshold_value = fields.Float(string='Threshold Value', digits=(16, 4))
    unit = fields.Char(string='Unit', default='ms')
    model_name = fields.Char(string='Related Model')
    endpoint = fields.Char(string='Related Endpoint / URL')
    cron_id = fields.Many2one('ir.cron', string='Related Cron Job', ondelete='set null')

    # ─── Notification tracking ─────────────────────────────────
    notification_sent = fields.Boolean(
        string='Notification Sent',
        default=False,
        help='True when at least one notification (email/Slack) was dispatched.',
    )
    notification_log = fields.Text(
        string='Notification Log',
        help='JSON log of all notifications sent for this alert.',
    )

    # ─── Resolution ────────────────────────────────────────────
    resolved_by = fields.Many2one('res.users', string='Resolved By', readonly=True)
    resolved_date = fields.Datetime(string='Resolved Date', readonly=True)
    resolution_note = fields.Text(string='Resolution Note', tracking=True)

    # ─── Computed ──────────────────────────────────────────────
    age_hours = fields.Float(
        string='Age (hours)',
        compute='_compute_age',
    )

    @api.depends('create_date')
    def _compute_age(self):
        now = fields.Datetime.now()
        for rec in self:
            if rec.create_date:
                delta = now - rec.create_date
                rec.age_hours = round(delta.total_seconds() / 3600, 2)
            else:
                rec.age_hours = 0.0

    # ─── Lifecycle actions ─────────────────────────────────────
    def action_acknowledge(self):
        """Mark alert as acknowledged by the current user."""
        self.write({'state': 'acknowledged'})
        self.message_post(body=_('Alert acknowledged by %s.') % self.env.user.name)

    def action_resolve(self):
        """Mark alert as resolved."""
        self.write({
            'state': 'resolved',
            'resolved_by': self.env.uid,
            'resolved_date': fields.Datetime.now(),
        })

    def action_mute(self):
        """Mute alert (suppresses further notifications for the same type)."""
        self.write({'state': 'muted'})

    def action_reopen(self):
        self.write({'state': 'open'})

    # ─── Factory ───────────────────────────────────────────────
    @api.model
    def _raise_alert_from_metric(self, metric):
        """
        Create an alert from a metric record, respecting cooldown.
        This is the main entry point called by sentinelle_metric._record_metric().
        """
        config = self.env['sentinelle.config'].get_active_config()
        if not config.monitoring_enabled:
            return

        # Map metric_type → alert_type
        type_map = {
            'orm_create':   'orm_performance',
            'orm_write':    'orm_performance',
            'orm_search':   'orm_performance',
            'sql_slow':     'sql_slow',
            'sql_count':    'sql_n_plus_one',
            'api_response': 'api_slow',
            'log_error':    'log_errors',
            'cron_delay':   'cron_delay',
            'cron_failure': 'cron_failure',
            'sys_cpu':      'sys_cpu',
            'sys_ram':      'sys_ram',
            'sys_disk':     'sys_disk',
            'custom':       'custom',
        }
        alert_type = type_map.get(metric.metric_type, 'custom')

        # Cooldown check: don't re-alert for the same type within cooldown window
        cooldown_minutes = config.alert_cooldown_minutes or 60
        cooldown_from = fields.Datetime.now() - timedelta(minutes=cooldown_minutes)
        recent = self.sudo().search([
            ('alert_type', '=', alert_type),
            ('state', 'in', ['open', 'acknowledged']),
            ('create_date', '>=', cooldown_from),
            ('model_name', '=', metric.model_name or False),
        ], limit=1)
        if recent:
            _logger.debug(
                'Sentinelle: alert for %s suppressed by cooldown (existing: %s)',
                alert_type, recent.id
            )
            return

        # Build a descriptive title and body
        title = self._build_alert_title(alert_type, metric)
        description = self._build_alert_description(metric)

        alert = self.sudo().create({
            'name': title,
            'alert_type': alert_type,
            'severity': metric.severity,
            'description': description,
            'metric_id': metric.id,
            'metric_value': metric.value,
            'threshold_value': metric.threshold_value,
            'unit': metric.unit,
            'model_name': metric.model_name,
            'endpoint': metric.endpoint,
            'cron_id': metric.cron_id.id if metric.cron_id else False,
        })

        # Dispatch notifications
        alert._send_notifications(config)
        return alert

    @api.model
    def _build_alert_title(self, alert_type, metric):
        titles = {
            'orm_performance': _('Slow ORM %s on %s (%.0f ms)') % (
                metric.metric_type.replace('orm_', ''), metric.model_name or '?', metric.value),
            'sql_slow':        _('Slow SQL Query (%.0f ms)') % metric.value,
            'sql_n_plus_one':  _('N+1 SQL Pattern Detected (%d queries)') % metric.value,
            'api_slow':        _('Slow External API Response (%.0f ms): %s') % (
                metric.value, metric.endpoint or '?'),
            'api_failure':     _('External API Failure: %s') % (metric.endpoint or '?'),
            'log_errors':      _('High Error Rate in Logs (%d errors/hour)') % metric.value,
            'cron_delay':      _('Cron Job Delayed: %s') % (
                metric.cron_id.name if metric.cron_id else '?'),
            'cron_failure':    _('Cron Job Failed: %s') % (
                metric.cron_id.name if metric.cron_id else '?'),
            'sys_cpu':         _('High CPU Usage: %.1f%%') % metric.value,
            'sys_ram':         _('High RAM Usage: %.1f%%') % metric.value,
            'sys_disk':        _('High Disk Usage: %.1f%%') % metric.value,
        }
        return titles.get(alert_type, metric.name)

    @api.model
    def _build_alert_description(self, metric):
        parts = [
            _('Metric: %s') % metric.name,
            _('Observed value: %.4f %s') % (metric.value, metric.unit),
            _('Threshold: %.4f %s') % (metric.threshold_value, metric.unit),
        ]
        if metric.model_name:
            parts.append(_('Model: %s') % metric.model_name)
        if metric.sql_query_preview:
            parts.append(_('SQL Preview: %s') % metric.sql_query_preview)
        if metric.endpoint:
            parts.append(_('Endpoint: %s') % metric.endpoint)
        return '\n'.join(parts)

    # ─── Notifications ─────────────────────────────────────────
    def _send_notifications(self, config):
        """Dispatch all configured notification channels."""
        self.ensure_one()
        log = []

        if config.notify_email and config.notify_email_addresses:
            result = self._notify_email(config)
            log.append({'channel': 'email', 'result': result})

        if config.notify_slack and config.slack_webhook_url:
            result = self._notify_slack(config)
            log.append({'channel': 'slack', 'result': result})

        if config.notify_odoo_channel and config.odoo_channel_id:
            result = self._notify_odoo_channel(config)
            log.append({'channel': 'odoo_channel', 'result': result})

        self.sudo().write({
            'notification_sent': bool(log),
            'notification_log': json.dumps(log),
        })

    def _notify_email(self, config):
        """Send alert by email using Odoo's mail system."""
        try:
            recipients = [
                e.strip() for e in (config.notify_email_addresses or '').split(',')
                if e.strip()
            ]
            if not recipients:
                return 'no_recipients'

            template_body = _(
                '<p><strong>🚨 Sentinelle Health Monitor Alert</strong></p>'
                '<p><strong>Alert:</strong> %(name)s</p>'
                '<p><strong>Severity:</strong> %(severity)s</p>'
                '<p><strong>Description:</strong></p><pre>%(description)s</pre>'
                '<p><em>This alert was generated automatically by Sentinelle Health Monitor.</em></p>'
            ) % {
                'name': self.name,
                'severity': dict(self._fields['severity'].selection).get(self.severity, self.severity),
                'description': self.description or '',
            }

            mail_values = {
                'subject': _('[Sentinelle] %s') % self.name,
                'body_html': template_body,
                'email_to': ','.join(recipients),
                'auto_delete': True,
            }
            mail = self.env['mail.mail'].sudo().create(mail_values)
            mail.send()
            return 'sent'
        except Exception as e:
            _logger.exception('Sentinelle: email notification failed: %s', e)
            return 'error: %s' % str(e)

    def _notify_slack(self, config):
        """Send alert to a Slack channel via incoming webhook."""
        try:
            import requests
            severity_emoji = {'info': '🔵', 'warning': '🟡', 'critical': '🔴'}.get(
                self.severity, '⚪'
            )
            payload = {
                'text': '%s *[Sentinelle Alert]* %s' % (severity_emoji, self.name),
                'attachments': [{
                    'color': {'info': '#36a64f', 'warning': '#ffcc00', 'critical': '#ff0000'}.get(
                        self.severity, '#cccccc'
                    ),
                    'fields': [
                        {'title': 'Severity', 'value': self.severity.upper(), 'short': True},
                        {'title': 'Type', 'value': self.alert_type, 'short': True},
                        {'title': 'Details', 'value': self.description or '', 'short': False},
                    ],
                    'footer': 'Sentinelle Health Monitor',
                }],
            }
            response = requests.post(
                config.slack_webhook_url,
                json=payload,
                timeout=5,
            )
            return 'sent' if response.status_code == 200 else 'http_%d' % response.status_code
        except Exception as e:
            _logger.exception('Sentinelle: Slack notification failed: %s', e)
            return 'error: %s' % str(e)

    def _notify_odoo_channel(self, config):
        """Post alert message to an Odoo Discuss channel."""
        try:
            channel = config.odoo_channel_id
            severity_emoji = {'info': '🔵', 'warning': '🟡', 'critical': '🔴'}.get(
                self.severity, '⚪'
            )
            msg = '%s <b>[Sentinelle]</b> %s<br/><pre>%s</pre>' % (
                severity_emoji, self.name, self.description or ''
            )
            channel.sudo().message_post(body=msg, subtype_xmlid='mail.mt_comment')
            return 'sent'
        except Exception as e:
            _logger.exception('Sentinelle: Odoo channel notification failed: %s', e)
            return 'error: %s' % str(e)

    @api.model
    def purge_old_alerts(self):
        """Called by cron: remove old resolved/muted alerts based on retention config."""
        config = self.env['sentinelle.config'].get_active_config()
        retention = config.alert_retention_days or 90
        cutoff = fields.Datetime.now() - timedelta(days=retention)
        old = self.search([
            ('state', 'in', ['resolved', 'muted']),
            ('create_date', '<', cutoff),
        ])
        count = len(old)
        old.unlink()
        _logger.info('Sentinelle: purged %d old alerts.', count)
        return count
