# -*- coding: utf-8 -*-
# sentinelle_health_monitor/models/sentinelle_api_monitor.py
"""
External API Response Time Monitor.

Provides two mechanisms:
1. A context manager / decorator `SentinelleApiMonitor.track()` that
   developers can wrap around any external HTTP call in their code.
2. A registry of known external endpoints that the cron job probes
   periodically with a lightweight HTTP HEAD/GET request.
"""

import time
import logging

from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)


class SentinelleApiEndpoint(models.Model):
    """
    Registry of external API endpoints to probe.
    Add records here to have Sentinelle periodically ping each endpoint
    and measure its response time.
    """
    _name = 'sentinelle.api.endpoint'
    _description = 'Sentinelle API Endpoint Registry'
    _order = 'name'

    name = fields.Char(string='Endpoint Name', required=True)
    url = fields.Char(
        string='URL',
        required=True,
        help='Full URL to probe, e.g. https://api.stripe.com/v1/charges',
    )
    method = fields.Selection(
        selection=[('GET', 'GET'), ('HEAD', 'HEAD'), ('POST', 'POST')],
        string='HTTP Method',
        default='GET',
    )
    active = fields.Boolean(default=True)
    timeout_seconds = fields.Integer(default=10)
    expected_status_code = fields.Integer(
        default=200,
        help='HTTP status code that counts as a successful response.',
    )
    consecutive_failures = fields.Integer(
        string='Consecutive Failures',
        default=0,
        readonly=True,
    )
    last_probe_date = fields.Datetime(string='Last Probed', readonly=True)
    last_response_ms = fields.Float(string='Last Response Time (ms)', readonly=True)

    def action_probe_now(self):
        """Allow manual probing from the form view."""
        monitor = self.env['sentinelle.api.monitor']
        for endpoint in self:
            monitor._probe_endpoint(endpoint)


class SentinelleApiMonitor(models.Model):
    """
    Service model: runs API probes and provides the track() context manager.
    """
    _name = 'sentinelle.api.monitor'
    _description = 'Sentinelle API Monitor Service'

    @api.model
    def run_api_probes(self):
        """
        Cron entry point: probe all active registered endpoints.
        """
        config = self.env['sentinelle.config'].get_active_config()
        if not config.monitoring_enabled:
            return

        endpoints = self.env['sentinelle.api.endpoint'].search([('active', '=', True)])
        for endpoint in endpoints:
            self._probe_endpoint(endpoint)

        _logger.info('Sentinelle: API probes completed for %d endpoints.', len(endpoints))

    @api.model
    def _probe_endpoint(self, endpoint):
        """
        Probe a single endpoint and record the metric.
        Updates consecutive_failures on the endpoint record.
        """
        config = self.env['sentinelle.config'].get_active_config()
        threshold_ms = config.api_response_threshold_ms or 3000
        failure_threshold = config.api_failure_threshold or 5

        try:
            import requests
            start = time.perf_counter()
            resp = requests.request(
                method=endpoint.method,
                url=endpoint.url,
                timeout=endpoint.timeout_seconds or 10,
                allow_redirects=True,
            )
            elapsed_ms = (time.perf_counter() - start) * 1000
            success = (resp.status_code == endpoint.expected_status_code)

        except Exception as exc:
            elapsed_ms = (endpoint.timeout_seconds or 10) * 1000
            success = False
            _logger.warning('Sentinelle API probe failed for %s: %s', endpoint.url, exc)

        Metric = self.env['sentinelle.metric'].sudo()

        if success:
            failures = 0
            severity = 'warning' if elapsed_ms > threshold_ms else 'info'
            Metric._record_metric(
                metric_type='api_response',
                name='API probe: %s' % endpoint.name,
                value=round(elapsed_ms, 2),
                unit='ms',
                threshold_value=float(threshold_ms),
                endpoint=endpoint.url,
                severity=severity,
            )
        else:
            failures = endpoint.consecutive_failures + 1
            severity = 'critical' if failures >= failure_threshold else 'warning'
            Metric._record_metric(
                metric_type='api_response',
                name='API FAILURE: %s' % endpoint.name,
                value=round(elapsed_ms, 2),
                unit='ms',
                threshold_value=float(threshold_ms),
                endpoint=endpoint.url,
                severity=severity,
            )

        endpoint.sudo().write({
            'consecutive_failures': failures,
            'last_probe_date': fields.Datetime.now(),
            'last_response_ms': round(elapsed_ms, 2),
        })

    @api.model
    def track_call(self, endpoint_name, url, elapsed_ms):
        """
        Public API for developers to manually report an external API call.
        Call this from your integration code after you've made the HTTP request:

            monitor = self.env['sentinelle.api.monitor']
            monitor.track_call(
                endpoint_name='Stripe Charge',
                url='https://api.stripe.com/v1/charges',
                elapsed_ms=350.0,
            )
        """
        config = self.env['sentinelle.config'].get_active_config()
        if not config.monitoring_enabled:
            return
        threshold_ms = config.api_response_threshold_ms or 3000
        severity = 'warning' if elapsed_ms > threshold_ms else 'info'
        self.env['sentinelle.metric'].sudo()._record_metric(
            metric_type='api_response',
            name='API call: %s' % endpoint_name,
            value=round(elapsed_ms, 2),
            unit='ms',
            threshold_value=float(threshold_ms),
            endpoint=url,
            severity=severity,
        )
