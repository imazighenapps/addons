# -*- coding: utf-8 -*-
# sentinelle_health_monitor/models/sentinelle_system_monitor.py
"""
System Resource Monitor.

Uses the `psutil` library to collect:
- CPU usage (%)
- RAM usage (%)
- Disk usage (%) for the partition hosting Odoo's data directory

psutil is listed as a Python dependency in __manifest__.py.
If not installed, the monitor degrades gracefully with a warning.
"""

import logging

from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)


def _get_psutil():
    """Lazy import psutil; return None if not installed."""
    try:
        import psutil
        return psutil
    except ImportError:
        _logger.warning(
            'Sentinelle: psutil is not installed. '
            'System resource monitoring is disabled. '
            'Install it with: pip install psutil'
        )
        return None


class SentinelleSystemMonitor(models.Model):
    """
    Collects CPU, RAM and disk metrics via psutil.
    Called by a scheduled action every N minutes.
    """
    _name = 'sentinelle.system.monitor'
    _description = 'Sentinelle System Resource Monitor'

    @api.model
    def run_system_checks(self):
        """
        Cron entry point.
        Collects all system metrics and records them.
        """
        config = self.env['sentinelle.config'].get_active_config()
        if not config.monitoring_enabled:
            return

        psutil = _get_psutil()
        if not psutil:
            return

        Metric = self.env['sentinelle.metric'].sudo()

        # ── CPU ─────────────────────────────────────────────
        try:
            # interval=1: blocks for 1 second to get a real measurement
            cpu_pct = psutil.cpu_percent(interval=1)
            threshold = config.cpu_usage_threshold_pct or 85.0
            severity = 'critical' if cpu_pct >= threshold * 1.1 else (
                'warning' if cpu_pct >= threshold else 'info'
            )
            Metric._record_metric(
                metric_type='sys_cpu',
                name='CPU Usage: %.1f%%' % cpu_pct,
                value=round(cpu_pct, 2),
                unit='%',
                threshold_value=threshold,
                severity=severity,
            )
        except Exception as e:
            _logger.error('Sentinelle: CPU metric collection failed: %s', e)

        # ── RAM ─────────────────────────────────────────────
        try:
            mem = psutil.virtual_memory()
            ram_pct = mem.percent
            threshold = config.ram_usage_threshold_pct or 85.0
            severity = 'critical' if ram_pct >= threshold * 1.1 else (
                'warning' if ram_pct >= threshold else 'info'
            )
            Metric._record_metric(
                metric_type='sys_ram',
                name='RAM Usage: %.1f%% (%.1f GB used / %.1f GB total)' % (
                    ram_pct,
                    mem.used / (1024 ** 3),
                    mem.total / (1024 ** 3),
                ),
                value=round(ram_pct, 2),
                unit='%',
                threshold_value=threshold,
                severity=severity,
            )
        except Exception as e:
            _logger.error('Sentinelle: RAM metric collection failed: %s', e)

        # ── Disk ─────────────────────────────────────────────
        try:
            # Monitor the root partition. Adapt path per deployment.
            disk_path = self._get_data_dir_path()
            disk = psutil.disk_usage(disk_path)
            disk_pct = disk.percent
            threshold = config.disk_usage_threshold_pct or 90.0
            severity = 'critical' if disk_pct >= threshold * 1.05 else (
                'warning' if disk_pct >= threshold else 'info'
            )
            Metric._record_metric(
                metric_type='sys_disk',
                name='Disk Usage: %.1f%% (%.1f GB free / %.1f GB total) — %s' % (
                    disk_pct,
                    disk.free / (1024 ** 3),
                    disk.total / (1024 ** 3),
                    disk_path,
                ),
                value=round(disk_pct, 2),
                unit='%',
                threshold_value=threshold,
                severity=severity,
            )
        except Exception as e:
            _logger.error('Sentinelle: Disk metric collection failed: %s', e)

        # ── Per-CPU load (informational) ─────────────────────
        try:
            per_cpu = psutil.cpu_percent(interval=None, percpu=True)
            max_core = max(per_cpu) if per_cpu else 0
            if max_core > (config.cpu_usage_threshold_pct or 85.0):
                Metric._record_metric(
                    metric_type='sys_cpu',
                    name='CPU Core Hotspot: %.1f%% on core %d' % (
                        max_core, per_cpu.index(max_core)
                    ),
                    value=round(max_core, 2),
                    unit='%',
                    threshold_value=config.cpu_usage_threshold_pct or 85.0,
                    severity='warning',
                )
        except Exception:
            pass  # non-critical

        _logger.info('Sentinelle: system resource checks completed.')

    @api.model
    def _get_data_dir_path(self):
        """
        Return the path to monitor for disk usage.
        Defaults to the Odoo data directory if accessible, else '/'.
        Override this method for custom deployment paths.
        """
        import os
        try:
            from odoo.tools import config as odoo_config
            data_dir = odoo_config.get('data_dir', '/')
            if data_dir and os.path.exists(data_dir):
                return data_dir
        except Exception:
            pass
        return '/'
