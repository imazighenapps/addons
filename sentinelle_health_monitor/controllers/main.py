# -*- coding: utf-8 -*-

import json
import logging
from datetime import timedelta
from collections import defaultdict

from odoo import fields, http
from odoo.http import request

_logger = logging.getLogger(__name__)

_TYPE_COLORS = {
    'orm_performance': '#3B6FE8', 'sql_slow': '#F59E0B',
    'sql_n_plus_one': '#F97316', 'api_slow': '#8B5CF6',
    'api_failure': '#DC2626', 'log_errors': '#EC4899',
    'cron_delay': '#14B8A6', 'cron_failure': '#EF4444',
    'sys_cpu': '#10B981', 'sys_ram': '#6366F1',
    'sys_disk': '#F43F5E', 'custom': '#94A3B8',
}

_TYPE_LABELS = {
    'orm_performance': 'ORM Performance', 'sql_slow': 'SQL Lente',
    'sql_n_plus_one': 'N+1 SQL', 'api_slow': 'API Lente',
    'api_failure': 'Echec API', 'log_errors': 'Erreurs Log',
    'cron_delay': 'Retard Cron', 'cron_failure': 'Echec Cron',
    'sys_cpu': 'CPU Elevé', 'sys_ram': 'RAM Elevée',
    'sys_disk': 'Disque Elevé', 'custom': 'Personnalisé',
}


def _sf(val, default=0.0):
    try:
        return round(float(val), 2) if val is not None else default
    except (TypeError, ValueError):
        return default


class SentinelleDashboardController(http.Controller):

    @http.route('/sentinelle/dashboard/data', type='json', auth='user', methods=['POST'])
    def dashboard_data(self, **kwargs):
        try:
            env = request.env
            now = fields.Datetime.now()
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            one_hour_ago = now - timedelta(hours=1)
            one_day_ago = now - timedelta(hours=24)
            return {
                'kpis':           self._kpis(env, now, today_start, one_hour_ago, one_day_ago),
                'recent_alerts':  self._recent_alerts(env),
                'metric_history': self._metric_history(env, one_day_ago, one_hour_ago),
                'system_stats':   self._system_stats(env),
                'cron_stats':     self._cron_stats(env, now),           # clé attendue par JS
                'alerts_by_type': self._alerts_by_type(env, one_day_ago),
                'alert_trend':    self._alert_trend(env, now),          # clé attendue par JS
            }
        except Exception as exc:
            _logger.exception('Sentinelle dashboard/data error: %s', exc)
            return {
                'kpis': {}, 'recent_alerts': [], 'metric_history': {},
                'system_stats': {}, 'cron_stats': [], 'alerts_by_type': [],
                'alert_trend': [], 'error': str(exc),
            }

    # ──────────────────────────────────────────────────────────────────────────
    def _kpis(self, env, now, today_start, h1, d1):
        A = env['sentinelle.alert']
        M = env['sentinelle.metric']
        cr = env.cr

        open_critical    = A.search_count([('state', '=', 'open'), ('severity', '=', 'critical')])
        open_warning     = A.search_count([('state', '=', 'open'), ('severity', '=', 'warning')])
        total_open       = A.search_count([('state', '=', 'open')])
        alerts_today     = A.search_count([('create_date', '>=', today_start)])
        resolved_today   = A.search_count([('state', '=', 'resolved'), ('create_date', '>=', today_start)])
        metrics_exceeded = M.search_count([('exceeded_threshold', '=', True), ('create_date', '>=', h1)])

        cr.execute("""
            SELECT metric_type, AVG(value) AS avg_val
            FROM sentinelle_metric
            WHERE metric_type IN ('orm_create','orm_write','orm_search')
              AND create_date >= %(since)s
            GROUP BY metric_type
        """, {'since': h1})
        orm = {r['metric_type']: _sf(r['avg_val']) for r in cr.dictfetchall()}

        slow_sql = M.search_count([('metric_type', '=', 'sql_slow'),
                                   ('exceeded_threshold', '=', True), ('create_date', '>=', h1)])
        api_fail = A.search_count([('alert_type', '=', 'api_failure'), ('create_date', '>=', h1)])

        cr.execute(
            "SELECT COUNT(*) FROM ir_logging WHERE level IN ('ERROR','CRITICAL') AND create_date >= %(s)s",
            {'s': h1},
        )
        log_err = int((cr.fetchone() or [0])[0])

        cr.execute("""
            SELECT alert_type, severity, COUNT(*) AS cnt
            FROM sentinelle_alert
            WHERE alert_type IN ('sys_cpu','sys_ram','sys_disk') AND create_date >= %(s)s
            GROUP BY alert_type, severity
        """, {'s': d1})
        sys_c = {}
        for r in cr.dictfetchall():
            k = '%s_%s' % (
                r['alert_type'].replace('sys_', ''),
                'alerts' if r['severity'] == 'critical' else 'warns',
            )
            sys_c[k] = int(r['cnt'])

        total_crons = env['ir.cron'].search_count([('active', '=', True)])
        config = env['sentinelle.config'].get_active_config()
        delay_min = config.cron_delay_threshold_minutes or 30
        cutoff = now - timedelta(minutes=delay_min)
        delayed = env['ir.cron'].sudo().search_count([
            ('active', '=', True), ('nextcall', '<', cutoff),
        ])
        failing = A.search_count([('alert_type', '=', 'cron_failure'), ('state', '=', 'open')])
        cron_a24 = A.search_count([
            ('alert_type', 'in', ['cron_delay', 'cron_failure']),
            ('create_date', '>=', d1),
        ])

        res = {
            'open_critical':    open_critical,
            'open_warning':     open_warning,
            'total_open':       total_open,
            'alerts_today':     alerts_today,
            'resolved_today':   resolved_today,
            'metrics_exceeded': metrics_exceeded,
            'avg_orm_create':   orm.get('orm_create'),
            'avg_orm_write':    orm.get('orm_write'),
            'avg_orm_search':   orm.get('orm_search'),
            'slow_sql_count':   slow_sql,
            'api_failures':     api_fail,
            'log_errors_1h':    log_err,
            'total_crons':      total_crons,
            'delayed_crons':    delayed,
            'failing_crons':    failing,
            'cron_alerts_24h':  cron_a24,
        }
        res.update({'sys_%s' % k: v for k, v in sys_c.items()})
        return res

    # ──────────────────────────────────────────────────────────────────────────
    def _recent_alerts(self, env):
        alerts = env['sentinelle.alert'].search(
            [('state', 'in', ['open', 'acknowledged'])],
            order='create_date desc', limit=20,
        )
        return [{
            'id':           a.id,
            'name':         a.name,
            'alert_type':   a.alert_type,
            'severity':     a.severity,
            'state':        a.state,
            'metric_value': _sf(a.metric_value),
            'unit':         a.unit or '',
            'create_date':  fields.Datetime.to_string(a.create_date) if a.create_date else '',
        } for a in alerts]

    # ──────────────────────────────────────────────────────────────────────────
    def _metric_history(self, env, d1, h1):
        """
        Retourne un dict avec les clés attendues par le JS :
          orm_create, orm_write, orm_search → [{value, name}]
          sql_slow   → [{value, sql_query_preview, name}]   (correction : expose sql_query_preview)
          api        → [{value, name, endpoint}]
          log_errors → [{model_name, value}]                 (correction : field model_name)
          cpu, ram   → [{value}]
        """
        cr = env.cr
        h = {}

        # ORM — 3 séries séparées (attendues par _drawOrm())
        for mtype in ('orm_create', 'orm_write', 'orm_search'):
            cr.execute("""
                SELECT value, model_name, name
                FROM sentinelle_metric
                WHERE metric_type = %(t)s
                ORDER BY create_date DESC LIMIT 30
            """, {'t': mtype})
            h[mtype] = [
                {'value': _sf(r['value']), 'name': r.get('model_name') or r.get('name', '')}
                for r in reversed(cr.dictfetchall())
            ]

        # SQL lentes — expose sql_query_preview (attendu par XML)
        cr.execute("""
            SELECT value, sql_query_preview, name
            FROM sentinelle_metric
            WHERE metric_type = 'sql_slow' AND create_date >= %(s)s
            ORDER BY value DESC LIMIT 10
        """, {'s': d1})
        h['sql_slow'] = [{
            'value':             _sf(r['value']),
            'sql_query_preview': (r.get('sql_query_preview') or r.get('name') or '')[:120],
            'name':              r.get('name', ''),
        } for r in cr.dictfetchall()]

        # API — expose endpoint (attendu par XML)
        cr.execute("""
            SELECT value, endpoint, name
            FROM sentinelle_metric
            WHERE metric_type = 'api_response'
            ORDER BY create_date DESC LIMIT 20
        """)
        h['api'] = [{
            'value':    _sf(r['value']),
            'name':     r.get('name', ''),
            'endpoint': r.get('endpoint', ''),
        } for r in cr.dictfetchall()]

        # Erreurs de log — expose model_name + value (attendus par XML)
        cr.execute("""
            SELECT model_name, SUM(value) AS tv, name
            FROM sentinelle_metric
            WHERE metric_type = 'log_error' AND create_date >= %(s)s
            GROUP BY model_name, name
            ORDER BY tv DESC LIMIT 8
        """, {'s': h1})
        h['log_errors'] = [{
            'model_name': r.get('model_name') or r.get('name', '?'),
            'value':      _sf(r['tv']),
        } for r in cr.dictfetchall()]

        # Sparklines système
        for mtype, key in (('sys_cpu', 'cpu'), ('sys_ram', 'ram')):
            cr.execute(
                "SELECT value FROM sentinelle_metric WHERE metric_type = %(t)s ORDER BY create_date DESC LIMIT 30",
                {'t': mtype},
            )
            h[key] = [{'value': _sf(r[0])} for r in reversed(cr.fetchall())]

        return h

    # ──────────────────────────────────────────────────────────────────────────
    def _system_stats(self, env):
        cr = env.cr
        s = {}

        for mtype, key in (('sys_cpu', 'cpu_pct'), ('sys_ram', 'ram_pct'), ('sys_disk', 'disk_pct')):
            cr.execute(
                "SELECT value FROM sentinelle_metric WHERE metric_type = %(t)s ORDER BY create_date DESC LIMIT 1",
                {'t': mtype},
            )
            row = cr.fetchone()
            s[key] = _sf(row[0]) if row else 0.0

        # Correction : suppression du _logger.warning de debug
        cr.execute(
            "SELECT extra_data FROM sentinelle_metric WHERE metric_type = 'sys_ram' ORDER BY create_date DESC LIMIT 1"
        )
        row = cr.fetchone()
        if row and row[0]:
            try:
                extra = json.loads(row[0])
                s.update({k: _sf(extra.get(k)) for k in ('ram_used_gb', 'ram_total_gb', 'disk_free_gb')})
            except Exception:
                pass

        try:
            cr.execute("SELECT pg_database_size(current_database()) / 1024.0 / 1024.0 AS mb")
            row = cr.fetchone()
            s['db_size_mb'] = _sf(row[0]) if row else 0.0
        except Exception:
            s['db_size_mb'] = 0.0

        try:
            cr.execute("""
                    SELECT
                        c.relname AS table_name,
                        pg_total_relation_size(c.oid) / 1048576.0 AS size_mb,
                        pg_size_pretty(pg_total_relation_size(c.oid)) AS total_size
                    FROM pg_class c
                    JOIN pg_namespace n ON n.oid = c.relnamespace
                    WHERE c.relkind = 'r'
                    AND n.nspname NOT IN ('pg_catalog','information_schema')
                    ORDER BY size_mb DESC
                    LIMIT 15
                """)

            s['table_sizes'] = [{
                    'table_name': r['table_name'],
                    'size_mb': _sf(r['size_mb']),
                    'total_size': r['total_size'],
                } for r in cr.dictfetchall()]

        except Exception as e:
                cr.rollback()
                _logger.warning("Sentinelle table size query failed: %s", e)
                s['table_sizes'] = []
                
        return s

    # ──────────────────────────────────────────────────────────────────────────
    def _cron_stats(self, env, now):
        """
        Retourne la liste des crons avec le champ 'delay_minutes'
        (correction : le JS et l'XML attendent delay_minutes, pas delay_min).
        """
        config = env['sentinelle.config'].get_active_config()
        delay_threshold = config.cron_delay_threshold_minutes or 30
        fail_threshold  = config.cron_failure_threshold or 3
        crons = env['ir.cron'].sudo().search([('active', '=', True)], limit=50)
        result = []

        for c in crons:
            delay   = 0.0
            status  = 'ok'
            if c.nextcall:
                delay = (now - c.nextcall).total_seconds() / 60
                if delay > delay_threshold * 3:
                    status = 'critical'
                elif delay > delay_threshold:
                    status = 'warning'
                else:
                    delay = 0.0

            env.cr.execute("""
                SELECT COUNT(*) FROM ir_logging
                WHERE level IN ('ERROR','CRITICAL') AND create_date >= %(s)s
                  AND (message ILIKE %(n)s OR func ILIKE %(n)s)
            """, {'s': now - timedelta(hours=6), 'n': '%%%s%%' % c.name})
            fail_count = int((env.cr.fetchone() or [0])[0])

            if fail_count >= fail_threshold:
                status = 'critical'

            result.append({
                'id':              c.id,
                'name':            c.name,
                'nextcall':        fields.Datetime.to_string(c.nextcall) if c.nextcall else None,
                'delay_minutes':   round(delay, 1),   # CORRECTION : delay_minutes (pas delay_min)
                'failure_count':   fail_count,
                'interval_number': c.interval_number,
                'interval_type':   c.interval_type,
                'status':          status,
            })

        result.sort(key=lambda r: {'critical': 0, 'warning': 1, 'ok': 2}[r['status']])
        return result

    # ──────────────────────────────────────────────────────────────────────────
    def _alerts_by_type(self, env, d1):
        """
        Retourne {label, value, color}.
        CORRECTION : champ nommé 'value' (attendu par JS et Chart.js doughnut).
        """
        env.cr.execute("""
            SELECT alert_type, COUNT(*) AS cnt
            FROM sentinelle_alert
            WHERE create_date >= %(s)s
            GROUP BY alert_type ORDER BY cnt DESC LIMIT 12
        """, {'s': d1})
        return [{
            'label': _TYPE_LABELS.get(r['alert_type'], r['alert_type']),
            'value': int(r['cnt']),                                      # 'value' pas 'count'
            'color': _TYPE_COLORS.get(r['alert_type'], '#94A3B8'),
        } for r in env.cr.dictfetchall()]

    # ──────────────────────────────────────────────────────────────────────────
    def _alert_trend(self, env, now):
        """
        Clé retournée : 'alert_trend' (attendue par JS _apply()).
        """
        try:
            env.cr.execute("""
                SELECT DATE_TRUNC('hour', create_date) AS hour, severity, COUNT(*) AS cnt
                FROM sentinelle_alert
                WHERE create_date >= %(s)s
                GROUP BY hour, severity ORDER BY hour
            """, {'s': now - timedelta(hours=24)})
            rows = env.cr.dictfetchall()
        except Exception as exc:
            _logger.warning('Sentinelle: alert trend query failed: %s', exc)
            return []

        buckets = defaultdict(lambda: {'count': 0, 'critical': 0, 'warning': 0, 'info': 0})
        for r in rows:
            h = str(r['hour'])[:13]
            sev = r.get('severity', 'info')
            cnt = int(r['cnt'])
            buckets[h][sev] = buckets[h].get(sev, 0) + cnt
            buckets[h]['count'] += cnt

        result = []
        for i in range(24, 0, -1):
            slot = now - timedelta(hours=i)
            key  = slot.strftime('%Y-%m-%d %H')
            b    = buckets.get(key, {})
            result.append({
                'hour':     key,
                'count':    b.get('count', 0),
                'critical': b.get('critical', 0),
                'warning':  b.get('warning', 0),
                'info':     b.get('info', 0),
            })
        return result

    # ──────────────────────────────────────────────────────────────────────────
    @http.route('/sentinelle/alert/<int:alert_id>/acknowledge',
                type='json', auth='user', methods=['POST'])
    def acknowledge_alert(self, alert_id, **kwargs):
        try:
            a = request.env['sentinelle.alert'].browse(alert_id)
            if not a.exists():
                return {'status': 'error', 'message': 'Alerte introuvable'}
            a.action_acknowledge()
            return {'status': 'ok'}
        except Exception as exc:
            _logger.error('Sentinelle: ack alert %s failed: %s', alert_id, exc)
            return {'status': 'error', 'message': str(exc)}