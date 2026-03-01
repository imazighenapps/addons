# -*- coding: utf-8 -*-
# sentinelle_health_monitor/models/sentinelle_sql_monitor.py
"""
SQL Performance Monitor.

Queries the PostgreSQL pg_stat_statements extension (if available) and
pg_stat_activity to surface slow queries without needing to patch the
Odoo cursor or ORM.

Falls back to a simpler pg_stat_activity scan if pg_stat_statements is
not installed on the target database.
"""

import logging
from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)

# SQL to retrieve slow queries from pg_stat_statements (requires the extension)
_PG_STAT_STATEMENTS_SQL = """
    SELECT
        queryid,
        LEFT(query, 500)    AS query_preview,
        calls,
        total_exec_time / calls AS avg_exec_time_ms,
        max_exec_time           AS max_exec_time_ms,
        rows / NULLIF(calls, 0) AS avg_rows
    FROM pg_stat_statements
    WHERE
        dbid = (SELECT oid FROM pg_database WHERE datname = current_database())
        AND calls > 0
        AND total_exec_time / calls > %(threshold_ms)s
        AND query NOT LIKE '%%pg_stat%%'       -- exclude monitoring queries
        AND query NOT LIKE '%%sentinelle%%'    -- exclude our own queries
    ORDER BY avg_exec_time_ms DESC
    LIMIT 20;
"""

# Fallback: look at currently running long queries
_PG_ACTIVITY_SQL = """
    SELECT
        pid,
        NOW() - query_start AS duration,
        LEFT(query, 500)    AS query_preview,
        state
    FROM pg_stat_activity
    WHERE
        state = 'active'
        AND query_start IS NOT NULL
        AND NOW() - query_start > INTERVAL '%(threshold_s)s seconds'
        AND query NOT LIKE '%%pg_stat%%'
        AND query NOT LIKE '%%sentinelle%%'
    ORDER BY duration DESC
    LIMIT 10;
"""

# SQL to check overall table sizes (top tables by total size)
_TABLE_SIZE_SQL = """
    SELECT
        schemaname,
        tablename,
        pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS total_size,
        pg_total_relation_size(schemaname||'.'||tablename)                  AS total_bytes
    FROM pg_tables
    WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
    ORDER BY total_bytes DESC
    LIMIT 15;
"""


class SentinelleSqlMonitor(models.Model):
    """
    Cron-driven SQL monitor.
    Polls PostgreSQL statistics tables for slow queries and large tables.
    """
    _name = 'sentinelle.sql.monitor'
    _description = 'Sentinelle SQL Monitor'

    @api.model
    def run_sql_analysis(self):
        """
        Main entry point called by the SQL monitoring cron job.
        1. Try pg_stat_statements for historical slow queries.
        2. Check pg_stat_activity for currently running slow queries.
        3. Record metrics and generate alerts.
        """
        config = self.env['sentinelle.config'].get_active_config()
        if not config.monitoring_enabled:
            return

        threshold_ms = config.sql_slow_query_threshold_ms or 1000
        Metric = self.env['sentinelle.metric'].sudo()
        cr = self.env.cr

        # ── 1. pg_stat_statements ────────────────────────────
        has_stat_statements = self._check_pg_stat_statements(cr)
        if has_stat_statements:
            self._analyse_stat_statements(cr, threshold_ms, Metric, config)
        else:
            _logger.info(
                'Sentinelle SQL: pg_stat_statements not available. '
                'Consider running: CREATE EXTENSION pg_stat_statements;'
            )

        # ── 2. pg_stat_activity (running queries) ────────────
        self._analyse_stat_activity(cr, threshold_ms, Metric, config)

        # ── 3. Table sizes ───────────────────────────────────
        self._analyse_table_sizes(cr, Metric)

        _logger.info('Sentinelle: SQL analysis completed.')

    @api.model
    def _check_pg_stat_statements(self, cr):
        """Return True if pg_stat_statements extension is installed."""
        try:
            cr.execute(
                "SELECT 1 FROM pg_extension WHERE extname = 'pg_stat_statements';"
            )
            return bool(cr.fetchone())
        except Exception:
            return False

    @api.model
    def _analyse_stat_statements(self, cr, threshold_ms, Metric, config):
        """Parse pg_stat_statements for slow queries and record metrics."""
        try:
            cr.execute(_PG_STAT_STATEMENTS_SQL, {'threshold_ms': threshold_ms})
            rows = cr.dictfetchall()
        except Exception as e:
            _logger.warning('Sentinelle: pg_stat_statements query failed: %s', e)
            return

        for row in rows:
            avg_ms = float(row.get('avg_exec_time_ms') or 0)
            max_ms = float(row.get('max_exec_time_ms') or 0)
            severity = 'critical' if avg_ms > threshold_ms * 5 else 'warning'

            Metric._record_metric(
                metric_type='sql_slow',
                name='Slow SQL (avg %.0f ms, max %.0f ms)' % (avg_ms, max_ms),
                value=round(avg_ms, 2),
                unit='ms',
                threshold_value=float(threshold_ms),
                sql_query_preview=row.get('query_preview', ''),
                severity=severity,
            )

        _logger.info('Sentinelle SQL: found %d slow queries in pg_stat_statements.', len(rows))

    @api.model
    def _analyse_stat_activity(self, cr, threshold_ms, Metric, config):
        """Scan pg_stat_activity for queries currently exceeding the threshold."""
        threshold_s = threshold_ms / 1000.0
        try:
            cr.execute(_PG_ACTIVITY_SQL, {'threshold_s': threshold_s})
            rows = cr.dictfetchall()
        except Exception as e:
            _logger.warning('Sentinelle: pg_stat_activity query failed: %s', e)
            return

        for row in rows:
            duration = row.get('duration')
            if duration is None:
                continue
            elapsed_ms = duration.total_seconds() * 1000 if hasattr(duration, 'total_seconds') else 0
            severity = 'critical' if elapsed_ms > threshold_ms * 5 else 'warning'

            Metric._record_metric(
                metric_type='sql_slow',
                name='Active slow query (pid=%s, %.0f ms)' % (row.get('pid'), elapsed_ms),
                value=round(elapsed_ms, 2),
                unit='ms',
                threshold_value=float(threshold_ms),
                sql_query_preview=row.get('query_preview', ''),
                severity=severity,
            )

    @api.model
    def _analyse_table_sizes(self, cr, Metric):
        """Record top-10 table sizes as informational metrics."""
        try:
            cr.execute(_TABLE_SIZE_SQL)
            rows = cr.dictfetchall()
        except Exception as e:
            _logger.warning('Sentinelle: table size query failed: %s', e)
            return

        for row in rows:
            size_mb = (row.get('total_bytes') or 0) / (1024 * 1024)
            table = '%s.%s' % (row.get('schemaname', ''), row.get('tablename', ''))
            Metric._record_metric(
                metric_type='sys_disk',
                name='Table size: %s (%s)' % (table, row.get('total_size', '?')),
                value=round(size_mb, 2),
                unit='MB',
                threshold_value=0,   # informational only
                severity='info',
            )
