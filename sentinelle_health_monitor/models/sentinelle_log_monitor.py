# -*- coding: utf-8 -*-
# sentinelle_health_monitor/models/sentinelle_log_monitor.py
"""
Log Error Frequency Monitor.

Reads from ir.logging (Odoo's built-in log table) and counts
the frequency of ERROR/CRITICAL entries within a rolling time window.
Generates alerts when the count exceeds the configured threshold.
"""

import logging
from collections import defaultdict

from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)


class SentinelleLogMonitor(models.Model):
    """
    Analyses ir.logging to detect error spikes.
    Runs via cron; no external dependencies required.
    """
    _name = 'sentinelle.log.monitor'
    _description = 'Sentinelle Log Monitor'

    @api.model
    def run_log_analysis(self):
        """
        Cron entry point.
        Counts ERROR and CRITICAL log entries within the analysis window.
        Groups by `func` (module/function) to surface the top offenders.
        """
        config = self.env['sentinelle.config'].get_active_config()
        if not config.monitoring_enabled:
            return

        window_hours = config.log_analysis_window_hours or 1
        threshold = config.log_error_count_threshold or 10

        # Compute the start of the analysis window
        from datetime import timedelta
        window_start = fields.Datetime.now() - timedelta(hours=window_hours)

        # Query ir.logging directly via ORM (respects access rules)
        # ir.logging stores: create_date, level, message, func, path, line
        try:
            # Use SQL for performance — ir.logging can be very large
            self.env.cr.execute("""
                SELECT
                    func,
                    level,
                    COUNT(*)        AS error_count,
                    MAX(create_date) AS latest_occurrence
                FROM ir_logging
                WHERE
                    level IN ('ERROR', 'CRITICAL', 'WARNING')
                    AND create_date >= %(window_start)s
                GROUP BY func, level
                HAVING COUNT(*) >= %(min_count)s
                ORDER BY error_count DESC
                LIMIT 50
            """, {
                'window_start': window_start,
                'min_count': max(1, threshold // 5),  # surface even moderate spikes
            })
            rows = self.env.cr.dictfetchall()
        except Exception as e:
            _logger.error('Sentinelle Log Monitor: query failed: %s', e)
            return

        Metric = self.env['sentinelle.metric'].sudo()
        total_errors = 0

        for row in rows:
            count = int(row['error_count'])
            total_errors += count if row['level'] in ('ERROR', 'CRITICAL') else 0
            severity = self._compute_log_severity(row['level'], count, threshold)

            Metric._record_metric(
                metric_type='log_error',
                name='Log %s spike: %s (%d in %dh)' % (
                    row['level'], row['func'] or 'unknown',
                    count, window_hours,
                ),
                value=float(count),
                unit='count',
                threshold_value=float(threshold),
                model_name=row['func'],
                severity=severity,
            )

        # Summary metric: total error count in window
        Metric._record_metric(
            metric_type='log_error',
            name='Total log errors in last %dh' % window_hours,
            value=float(total_errors),
            unit='count',
            threshold_value=float(threshold),
            severity='critical' if total_errors >= threshold * 2
                     else ('warning' if total_errors >= threshold else 'info'),
        )

        _logger.info(
            'Sentinelle Log Monitor: %d unique error sources found, %d total errors.',
            len(rows), total_errors,
        )

    @api.model
    def _compute_log_severity(self, level, count, threshold):
        """Determine alert severity based on log level and count."""
        if level == 'CRITICAL':
            return 'critical'
        if level == 'ERROR':
            return 'critical' if count >= threshold * 2 else 'warning'
        return 'info'
