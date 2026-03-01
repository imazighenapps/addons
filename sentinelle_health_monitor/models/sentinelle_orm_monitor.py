# -*- coding: utf-8 -*-
# sentinelle_health_monitor/models/sentinelle_orm_monitor.py
"""
ORM Performance Monitor.

Strategy: instead of patching base Odoo models (fragile, upgrade-risky),
we expose a mixin `SentinelleOrmMixin` that developers can optionally inherit
in their critical models. Additionally, a dedicated cron job samples ORM
statistics through test operations on a sentinel model.

For passive monitoring without mixin inheritance, the cron-based approach
is used: a lightweight test record is created/written/searched and the
duration is measured. This avoids monkey-patching production ORM.
"""

import time
import logging

from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)


class SentinelleOrmProbe(models.Model):
    """
    Lightweight probe model used for ORM performance benchmarking.
    The cron job creates, writes and searches records here to measure
    real ORM overhead on the current database.
    """
    _name = 'sentinelle.orm.probe'
    _description = 'Sentinelle ORM Probe (internal benchmarking)'

    name = fields.Char(required=True)
    value = fields.Float()
    probe_date = fields.Datetime(default=fields.Datetime.now)


class SentinelleOrmMixin(models.AbstractModel):
    """
    Optional mixin for production models.
    Inherit this in models you want to monitor individually:

        class MyModel(models.Model, SentinelleOrmMixin):
            _name = 'my.model'
            ...

    This wraps create/write/search with timing decorators.
    Only models that explicitly opt-in are monitored this way.
    """
    _name = 'sentinelle.orm.mixin'
    _description = 'Sentinelle ORM Monitor Mixin'

    def _sentinelle_should_monitor(self):
        """
        Override in subclasses to conditionally disable monitoring.
        Return False to skip metric recording for a specific call.
        """
        config = self.env['sentinelle.config'].get_active_config()
        return config.monitoring_enabled

    @api.model_create_multi
    def create(self, vals_list):
        if not self._sentinelle_should_monitor():
            return super().create(vals_list)

        start = time.perf_counter()
        result = super().create(vals_list)
        elapsed_ms = (time.perf_counter() - start) * 1000

        config = self.env['sentinelle.config'].get_active_config()
        threshold = config.orm_create_threshold_ms

        self.env['sentinelle.metric'].sudo()._record_metric(
            metric_type='orm_create',
            name='ORM create: %s' % self._name,
            value=round(elapsed_ms, 2),
            unit='ms',
            threshold_value=threshold,
            model_name=self._name,
            record_count=len(vals_list),
            severity='warning' if elapsed_ms > threshold else 'info',
        )
        return result

    def write(self, vals):
        if not self._sentinelle_should_monitor():
            return super().write(vals)

        start = time.perf_counter()
        result = super().write(vals)
        elapsed_ms = (time.perf_counter() - start) * 1000

        config = self.env['sentinelle.config'].get_active_config()
        threshold = config.orm_write_threshold_ms

        self.env['sentinelle.metric'].sudo()._record_metric(
            metric_type='orm_write',
            name='ORM write: %s' % self._name,
            value=round(elapsed_ms, 2),
            unit='ms',
            threshold_value=threshold,
            model_name=self._name,
            record_count=len(self),
            severity='warning' if elapsed_ms > threshold else 'info',
        )
        return result

    @api.model
    def search(self, domain, offset=0, limit=None, order=None):
        if not self._sentinelle_should_monitor():
            return super().search(domain, offset=offset, limit=limit, order=order)

        start = time.perf_counter()
        result = super().search(domain, offset=offset, limit=limit, order=order)
        elapsed_ms = (time.perf_counter() - start) * 1000

        config = self.env['sentinelle.config'].get_active_config()
        threshold = config.orm_search_threshold_ms

        self.env['sentinelle.metric'].sudo()._record_metric(
            metric_type='orm_search',
            name='ORM search: %s' % self._name,
            value=round(elapsed_ms, 2),
            unit='ms',
            threshold_value=threshold,
            model_name=self._name,
            record_count=len(result),
            severity='warning' if elapsed_ms > threshold else 'info',
        )
        return result


class SentinelleOrmMonitor(models.Model):
    """
    Service model: runs ORM benchmark probes on demand or via cron.
    Does not inherit from the mixin (avoids recursive monitoring).
    """
    _name = 'sentinelle.orm.monitor'
    _description = 'Sentinelle ORM Monitor Service'

    @api.model
    def run_orm_benchmark(self):
        """
        Execute create / write / search benchmarks using the probe model.
        Called by the ORM monitoring cron job.
        Records metrics for each operation.
        """
        config = self.env['sentinelle.config'].get_active_config()
        if not config.monitoring_enabled:
            return

        Probe = self.env['sentinelle.orm.probe'].sudo()
        Metric = self.env['sentinelle.metric'].sudo()

        # ── Benchmark: create ────────────────────────────────
        try:
            start = time.perf_counter()
            probe = Probe.create({'name': 'sentinelle_probe_%s' % int(time.time()), 'value': 1.0})
            elapsed_ms = (time.perf_counter() - start) * 1000
            threshold = config.orm_create_threshold_ms
            Metric._record_metric(
                metric_type='orm_create',
                name='ORM Benchmark: create (sentinelle.orm.probe)',
                value=round(elapsed_ms, 2),
                unit='ms',
                threshold_value=threshold,
                model_name='sentinelle.orm.probe',
                record_count=1,
                severity='warning' if elapsed_ms > threshold else 'info',
            )
        except Exception as e:
            _logger.error('Sentinelle ORM benchmark (create) failed: %s', e)
            probe = None

        # ── Benchmark: write ─────────────────────────────────
        if probe:
            try:
                start = time.perf_counter()
                probe.write({'value': 2.0})
                elapsed_ms = (time.perf_counter() - start) * 1000
                threshold = config.orm_write_threshold_ms
                Metric._record_metric(
                    metric_type='orm_write',
                    name='ORM Benchmark: write (sentinelle.orm.probe)',
                    value=round(elapsed_ms, 2),
                    unit='ms',
                    threshold_value=threshold,
                    model_name='sentinelle.orm.probe',
                    record_count=1,
                    severity='warning' if elapsed_ms > threshold else 'info',
                )
            except Exception as e:
                _logger.error('Sentinelle ORM benchmark (write) failed: %s', e)

        # ── Benchmark: search ────────────────────────────────
        try:
            start = time.perf_counter()
            results = Probe.search([('name', 'like', 'sentinelle_probe_')], limit=100)
            elapsed_ms = (time.perf_counter() - start) * 1000
            threshold = config.orm_search_threshold_ms
            Metric._record_metric(
                metric_type='orm_search',
                name='ORM Benchmark: search (sentinelle.orm.probe)',
                value=round(elapsed_ms, 2),
                unit='ms',
                threshold_value=threshold,
                model_name='sentinelle.orm.probe',
                record_count=len(results),
                severity='warning' if elapsed_ms > threshold else 'info',
            )
        except Exception as e:
            _logger.error('Sentinelle ORM benchmark (search) failed: %s', e)

        # ── Cleanup old probe records (keep table small) ─────
        try:
            old_probes = Probe.search([('name', 'like', 'sentinelle_probe_')], limit=500)
            if len(old_probes) > 50:
                old_probes[:len(old_probes) - 10].unlink()
        except Exception:
            pass

        _logger.info('Sentinelle: ORM benchmark completed.')
