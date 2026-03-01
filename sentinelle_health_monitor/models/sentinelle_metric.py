# -*- coding: utf-8 -*-
# sentinelle_health_monitor/models/sentinelle_metric.py
"""
Generic Metric model.
All monitoring subsystems (ORM, SQL, API, System…) write records here.
Each record represents one data point collected at a specific moment in time.

Design philosophy: keep this model lean. Heavy aggregation happens in
_compute fields or SQL queries triggered from the dashboard controller.
"""

from odoo import api, fields, models, _


class SentinelleMetric(models.Model):
    """
    Time-series data point for any monitored metric.

    Extending: to add a new metric type, simply call:
        self.env['sentinelle.metric']._record_metric(
            metric_type='my_custom_metric',
            name='My Custom Metric',
            value=42.5,
            unit='ms',
            meta={'extra': 'info'},
        )
    """
    _name = 'sentinelle.metric'
    _description = 'Health Monitor Metric'
    _order = 'create_date desc'
    # Keep the table indexed on common filter columns
    _sql_constraints = []

    # ─── Identity ──────────────────────────────────────────────
    name = fields.Char(
        string='Metric Name',
        required=True,
        index=True,
        help='Human-readable label, e.g. "ORM create res.partner".',
    )
    metric_type = fields.Selection(
        selection=[
            ('orm_create',    'ORM Create'),
            ('orm_write',     'ORM Write'),
            ('orm_search',    'ORM Search'),
            ('sql_slow',      'Slow SQL Query'),
            ('sql_count',     'SQL Query Count'),
            ('api_response',  'External API Response'),
            ('log_error',     'Log Error Frequency'),
            ('cron_delay',    'Cron Job Delay'),
            ('cron_failure',  'Cron Job Failure'),
            ('sys_cpu',       'CPU Usage'),
            ('sys_ram',       'RAM Usage'),
            ('sys_disk',      'Disk Usage'),
            ('custom',        'Custom Metric'),
        ],
        string='Metric Type',
        required=True,
        index=True,
    )

    # ─── Value ─────────────────────────────────────────────────
    value = fields.Float(
        string='Value',
        required=True,
        digits=(16, 4),
        help='Numeric measurement (duration in ms, %, count, etc.).',
    )
    unit = fields.Char(
        string='Unit',
        default='ms',
        help='Unit of measure: ms, %, count, MB, etc.',
    )
    threshold_value = fields.Float(
        string='Threshold at Recording',
        help='The configured threshold at the time this metric was captured.',
    )
    exceeded_threshold = fields.Boolean(
        string='Threshold Exceeded',
        index=True,
        default=False,
    )

    # ─── Context ───────────────────────────────────────────────
    model_name = fields.Char(
        string='Odoo Model',
        index=True,
        help='Populated for ORM metrics, e.g. "res.partner".',
    )
    record_count = fields.Integer(
        string='Record Count',
        help='Number of records involved in the operation.',
    )
    sql_query_preview = fields.Text(
        string='SQL Query Preview',
        help='First 500 chars of the offending SQL query.',
    )
    endpoint = fields.Char(
        string='Endpoint / URL',
        help='For API metrics: the external URL called.',
    )
    cron_id = fields.Many2one(
        'ir.cron',
        string='Cron Job',
        ondelete='set null',
        help='For cron metrics: the related scheduled action.',
    )

    # ─── Metadata ──────────────────────────────────────────────
    extra_data = fields.Text(
        string='Extra Data (JSON)',
        help='Additional context stored as a JSON blob by the monitoring subsystem.',
    )
    severity = fields.Selection(
        selection=[
            ('info',     'Info'),
            ('warning',  'Warning'),
            ('critical', 'Critical'),
        ],
        string='Severity',
        default='info',
        index=True,
    )

    # ─── Business Methods ──────────────────────────────────────
    @api.model
    def _record_metric(self, metric_type, name, value, unit='ms',
                       threshold_value=0.0, model_name=None, record_count=0,
                       sql_query_preview=None, endpoint=None, cron_id=None,
                       extra_data=None, severity='info'):
        """
        Central factory method to create a metric record.
        Called by all monitoring subsystems.

        Returns the created record.
        Also triggers alert creation if threshold is exceeded.
        """
        exceeded = value > threshold_value if threshold_value else False
        if exceeded and severity == 'info':
            severity = 'warning'

        vals = {
            'name': name,
            'metric_type': metric_type,
            'value': value,
            'unit': unit,
            'threshold_value': threshold_value,
            'exceeded_threshold': exceeded,
            'model_name': model_name,
            'record_count': record_count,
            'sql_query_preview': (sql_query_preview or '')[:500],
            'endpoint': endpoint,
            'cron_id': cron_id,
            'extra_data': extra_data,
            'severity': severity,
        }
        metric = self.sudo().create(vals)

        if exceeded:
            self.env['sentinelle.alert']._raise_alert_from_metric(metric)

        return metric

    @api.model
    def purge_old_metrics(self):
        """
        Called by a scheduled action to clean up old metric records.
        Retention window comes from the active config.
        """
        config = self.env['sentinelle.config'].get_active_config()
        retention = config.metric_retention_days or 30
        cutoff = fields.Datetime.subtract(fields.Datetime.now(), days=retention)
        old = self.search([('create_date', '<', cutoff)])
        count = len(old)
        old.unlink()
        return count
