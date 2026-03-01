# -*- coding: utf-8 -*-
# sentinelle_health_monitor/models/sentinelle_notification.py
"""
Notification helper model.
Centralises all outbound notification logic not already in sentinelle_alert.py.
Provides:
  - digest emails (daily/weekly summary)
  - Extension hook: add_notification_channel() for custom channels
"""

import logging
from datetime import timedelta

from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)


class SentinelleNotification(models.Model):
    """
    Service model for digest notifications and notification extension hooks.
    """
    _name = 'sentinelle.notification'
    _description = 'Sentinelle Notification Service'

    @api.model
    def send_daily_digest(self):
        """
        Cron entry point: send a daily summary email to configured recipients.
        Summarises all alerts from the past 24 hours.
        """
        config = self.env['sentinelle.config'].get_active_config()
        if not config.monitoring_enabled or not config.notify_email:
            return

        since = fields.Datetime.now() - timedelta(hours=24)
        alerts = self.env['sentinelle.alert'].sudo().search([
            ('create_date', '>=', since),
        ])

        if not alerts:
            _logger.info('Sentinelle digest: no alerts in the last 24h.')
            return

        # Build summary
        by_severity = {}
        for alert in alerts:
            by_severity.setdefault(alert.severity, []).append(alert)

        lines = []
        for sev in ['critical', 'warning', 'info']:
            group = by_severity.get(sev, [])
            if group:
                emoji = {'critical': '🔴', 'warning': '🟡', 'info': '🔵'}.get(sev, '⚪')
                lines.append('<h3>%s %s (%d)</h3>' % (emoji, sev.upper(), len(group)))
                lines.append('<ul>')
                for a in group[:20]:  # cap at 20 per severity
                    lines.append('<li>%s — %s</li>' % (a.name, a.create_date))
                if len(group) > 20:
                    lines.append('<li>…and %d more</li>' % (len(group) - 20))
                lines.append('</ul>')

        body = (
            '<p><strong>📊 Sentinelle Daily Digest</strong></p>'
            '<p>Total alerts in the last 24h: <strong>%d</strong></p>%s'
            '<p><em>Sentinelle Health Monitor</em></p>'
        ) % (len(alerts), ''.join(lines))

        recipients = [
            e.strip() for e in (config.notify_email_addresses or '').split(',')
            if e.strip()
        ]
        if not recipients:
            return

        mail = self.env['mail.mail'].sudo().create({
            'subject': _('[Sentinelle] Daily Digest — %d alerts') % len(alerts),
            'body_html': body,
            'email_to': ','.join(recipients),
            'auto_delete': True,
        })
        mail.send()
        _logger.info('Sentinelle: daily digest sent to %s.', recipients)

    @api.model
    def register_notification_channel(self, name, callback):
        """
        Extension hook: register a custom notification channel.

        Usage (in another module):

            def my_pagerduty_notifier(alert, config):
                # call PagerDuty API here
                pass

            self.env['sentinelle.notification'].register_notification_channel(
                'pagerduty', my_pagerduty_notifier
            )

        The callback receives (alert_record, config_record) and should return
        a string status ('sent', 'error: ...').
        """
        if not hasattr(self.__class__, '_custom_channels'):
            self.__class__._custom_channels = {}
        self.__class__._custom_channels[name] = callback
        _logger.info('Sentinelle: registered custom notification channel: %s', name)

    @api.model
    def dispatch_custom_channels(self, alert, config):
        """
        Called by sentinelle_alert after built-in notifications.
        Dispatches to all registered custom channels.
        """
        channels = getattr(self.__class__, '_custom_channels', {})
        for name, callback in channels.items():
            try:
                result = callback(alert, config)
                _logger.info('Sentinelle custom channel %s: %s', name, result)
            except Exception as e:
                _logger.error('Sentinelle custom channel %s failed: %s', name, e)
