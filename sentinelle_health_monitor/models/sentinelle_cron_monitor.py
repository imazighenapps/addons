# -*- coding: utf-8 -*-
# sentinelle_health_monitor/models/sentinelle_cron_monitor.py
"""
Cron Job Health Monitor.

Checks all active ir.cron records for:
- Delayed execution (next_call is in the past beyond a threshold)
- Failure codes (cron records expose a 'code' and 'active' field; failed crons
  can be identified by checking the last run result via ir.logging)
"""

import logging
from datetime import timedelta

from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)


class SentinelleCronMonitor(models.Model):
    """
    Inspects ir.cron records and ir.logging to detect delayed or failing crons.
    """
    _name = 'sentinelle.cron.monitor'
    _description = 'Sentinelle Cron Monitor'

    @api.model
    def run_cron_analysis(self):
        """
        Cron entry point (runs periodically via its own scheduled action).
        Scans all active cron jobs and flags any that are delayed or failing.
        """
        config = self.env['sentinelle.config'].get_active_config()
        if not config.monitoring_enabled:
            return

        delay_threshold = config.cron_delay_threshold_minutes or 30
        failure_threshold = config.cron_failure_threshold or 3

        now = fields.Datetime.now()
        delay_cutoff = now - timedelta(minutes=delay_threshold)

        # Fetch all active cron jobs
        crons = self.env['ir.cron'].sudo().search([('active', '=', True)])
        Metric = self.env['sentinelle.metric'].sudo()

        delayed_count = 0
        for cron in crons:
            next_call = cron.nextcall
            if not next_call:
                continue

            # Check for delay
            if next_call < delay_cutoff:
                delay_minutes = (now - next_call).total_seconds() / 60
                delayed_count += 1
                severity = 'critical' if delay_minutes > delay_threshold * 3 else 'warning'
                Metric._record_metric(
                    metric_type='cron_delay',
                    name='Cron delayed: %s (%.0f min)' % (cron.name, delay_minutes),
                    value=round(delay_minutes, 1),
                    unit='minutes',
                    threshold_value=float(delay_threshold),
                    cron_id=cron.id,
                    severity=severity,
                )

            # Check for recent failures via ir.logging
            failure_count = self._count_cron_failures(cron, failure_threshold)
            if failure_count >= failure_threshold:
                Metric._record_metric(
                    metric_type='cron_failure',
                    name='Cron failing: %s (%d consecutive errors)' % (cron.name, failure_count),
                    value=float(failure_count),
                    unit='failures',
                    threshold_value=float(failure_threshold),
                    cron_id=cron.id,
                    severity='critical',
                )

        _logger.info(
            'Sentinelle Cron Monitor: checked %d crons, %d delayed.',
            len(crons), delayed_count,
        )

    @api.model
    def _count_cron_failures(self, cron, failure_threshold):
        """
        Count recent ERROR log entries associated with this cron job.
        ir.logging entries for crons typically have func = '<cron name>'.
        We look at the last (failure_threshold * 2) hours of logs.
        """
        window_start = fields.Datetime.now() - timedelta(hours=failure_threshold * 2)
        try:
            self.env.cr.execute("""
                SELECT COUNT(*) AS cnt
                FROM ir_logging
                WHERE
                    level IN ('ERROR', 'CRITICAL')
                    AND create_date >= %(window_start)s
                    AND (
                        message ILIKE %(cron_name)s
                        OR func ILIKE %(cron_name)s
                    )
            """, {
                'window_start': window_start,
                'cron_name': '%%%s%%' % cron.name,
            })
            row = self.env.cr.fetchone()
            return int(row[0]) if row else 0
        except Exception as e:
            _logger.warning('Sentinelle: cron failure count query failed: %s', e)
            return 0
