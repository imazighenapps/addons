# -*- coding: utf-8 -*-
# sentinelle_health_monitor/models/sentinelle_config.py
"""
Central configuration model for Sentinelle Health Monitor.
Stores thresholds, notification settings, and global switches.
This is the single source of truth for all monitoring parameters.
"""

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import json


class SentinelleConfig(models.Model):
    """
    Singleton-like configuration record for the health monitor.
    Only one active config record is expected (enforced by the UI).
    """
    _name = 'sentinelle.config'
    _description = 'Sentinelle Health Monitor Configuration'
    _order = 'id desc'

    # ─── General ───────────────────────────────────────────────
    name = fields.Char(
        string='Configuration Name',
        required=True,
        default='Default Configuration',
    )
    active = fields.Boolean(default=True)
    monitoring_enabled = fields.Boolean(
        string='Enable Monitoring',
        default=True,
        help='Master switch: disables all background monitoring when False.',
    )

    # ─── ORM Thresholds (milliseconds) ─────────────────────────
    orm_create_threshold_ms = fields.Integer(
        string='Max Create Time (ms)',
        default=500,
        help='Alert when an ORM create() call exceeds this duration.',
    )
    orm_write_threshold_ms = fields.Integer(
        string='Max Write Time (ms)',
        default=500,
    )
    orm_search_threshold_ms = fields.Integer(
        string='Max Search Time (ms)',
        default=300,
    )

    # ─── SQL Thresholds ────────────────────────────────────────
    sql_slow_query_threshold_ms = fields.Integer(
        string='Slow SQL Query Threshold (ms)',
        default=1000,
        help='Queries taking longer than this value are flagged as slow.',
    )
    sql_max_queries_per_request = fields.Integer(
        string='Max SQL Queries per Request',
        default=100,
        help='Alert when a single HTTP request generates more queries than this (N+1 detection).',
    )

    # ─── API Monitor ───────────────────────────────────────────
    api_response_threshold_ms = fields.Integer(
        string='Max External API Response Time (ms)',
        default=3000,
    )
    api_failure_threshold = fields.Integer(
        string='API Failure Count Threshold',
        default=5,
        help='Alert after this many consecutive failures to an external endpoint.',
    )

    # ─── Log Analysis ──────────────────────────────────────────
    log_error_count_threshold = fields.Integer(
        string='Error Log Count Threshold',
        default=10,
        help='Alert when this many unique errors appear within the analysis window.',
    )
    log_analysis_window_hours = fields.Integer(
        string='Log Analysis Window (hours)',
        default=1,
        help='Time window used when counting recent log errors.',
    )

    # ─── Cron Monitor ──────────────────────────────────────────
    cron_delay_threshold_minutes = fields.Integer(
        string='Cron Delay Threshold (minutes)',
        default=30,
        help='Alert when a scheduled action is delayed more than this duration.',
    )
    cron_failure_threshold = fields.Integer(
        string='Cron Failure Count Threshold',
        default=3,
        help='Alert when a cron job fails this many consecutive times.',
    )

    # ─── System Resources ──────────────────────────────────────
    cpu_usage_threshold_pct = fields.Float(
        string='CPU Usage Alert Threshold (%)',
        default=85.0,
    )
    ram_usage_threshold_pct = fields.Float(
        string='RAM Usage Alert Threshold (%)',
        default=85.0,
    )
    disk_usage_threshold_pct = fields.Float(
        string='Disk Usage Alert Threshold (%)',
        default=90.0,
    )

    # ─── Notification Channels ─────────────────────────────────
    notify_email = fields.Boolean(
        string='Email Notifications',
        default=True,
    )
    notify_email_addresses = fields.Char(
        string='Alert Email Recipients',
        help='Comma-separated list of email addresses.',
        default='admin@example.com',
    )
    notify_slack = fields.Boolean(
        string='Slack Notifications',
        default=False,
    )
    slack_webhook_url = fields.Char(
        string='Slack Webhook URL',
        help='Incoming webhook URL from your Slack App configuration.',
    )
    notify_odoo_channel = fields.Boolean(
        string='Odoo Channel Notifications',
        default=True,
    )
    odoo_channel_id = fields.Many2one(
        'discuss.channel',
        string='Odoo Discuss Channel',
        help='Post alerts to this Discuss channel.',
    )

    # ─── Alert Cooldown ────────────────────────────────────────
    alert_cooldown_minutes = fields.Integer(
        string='Alert Cooldown (minutes)',
        default=60,
        help='Minimum time between repeated alerts for the same issue, to prevent spam.',
    )

    # ─── Retention ─────────────────────────────────────────────
    metric_retention_days = fields.Integer(
        string='Metric Retention (days)',
        default=30,
        help='Metric records older than this are automatically purged.',
    )
    alert_retention_days = fields.Integer(
        string='Alert Retention (days)',
        default=90,
    )

    # ─── Extension hooks (JSON) ────────────────────────────────
    custom_thresholds = fields.Text(
        string='Custom Thresholds (JSON)',
        default='{}',
        help='JSON dict for custom metric thresholds added by extensions.',
    )

    # ─── Computed stats ────────────────────────────────────────
    total_alerts_today = fields.Integer(
        string='Alerts Today',
        compute='_compute_stats',
    )
    total_open_alerts = fields.Integer(
        string='Open Alerts',
        compute='_compute_stats',
    )

    @api.depends('monitoring_enabled')
    def _compute_stats(self):
        """Compute quick statistics shown on the config form."""
        from datetime import date
        today_start = fields.Datetime.now().replace(hour=0, minute=0, second=0)
        Alert = self.env['sentinelle.alert']
        for rec in self:
            rec.total_alerts_today = Alert.search_count([
                ('create_date', '>=', today_start),
            ])
            rec.total_open_alerts = Alert.search_count([
                ('state', 'in', ['open', 'acknowledged']),
            ])

    @api.constrains('custom_thresholds')
    def _check_custom_thresholds_json(self):
        """Validate that custom_thresholds contains valid JSON."""
        for rec in self:
            try:
                json.loads(rec.custom_thresholds or '{}')
            except (ValueError, TypeError):
                raise ValidationError(_('Custom Thresholds must be valid JSON.'))

    @api.constrains('cpu_usage_threshold_pct', 'ram_usage_threshold_pct', 'disk_usage_threshold_pct')
    def _check_percentage_thresholds(self):
        for rec in self:
            for fname, label in [
                ('cpu_usage_threshold_pct', 'CPU'),
                ('ram_usage_threshold_pct', 'RAM'),
                ('disk_usage_threshold_pct', 'Disk'),
            ]:
                val = rec[fname]
                if not (0.0 < val <= 100.0):
                    raise ValidationError(_(
                        '%s threshold must be between 0 and 100.', label
                    ))

    def get_active_config(self):
        """
        Helper: return the first active config, or create defaults.
        Use this in monitoring code: config = self.env['sentinelle.config'].get_active_config()
        """
        config = self.search([('active', '=', True)], limit=1)
        if not config:
            config = self.create({'name': 'Default Configuration'})
        return config

    def get_custom_threshold(self, key, default=None):
        """
        Extension hook: retrieve a custom threshold by key from the JSON blob.
        Usage: config.get_custom_threshold('my_metric_max_value', default=100)
        """
        self.ensure_one()
        try:
            data = json.loads(self.custom_thresholds or '{}')
            return data.get(key, default)
        except (ValueError, TypeError):
            return default
