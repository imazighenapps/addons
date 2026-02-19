# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ServerMonitorNetwork(models.Model):
    _name = 'server.monitor.network'
    _description = 'Network Monitoring by Interface'
    _order = 'timestamp desc'
    _rec_name = 'interface'

    history_id = fields.Many2one(
        'server.monitor.history',
        string='History',
        ondelete='cascade'
    )

    timestamp = fields.Datetime(
        string='Timestamp',
        required=True,
        default=fields.Datetime.now,
        index=True
    )

    interface = fields.Char(
        string='Interface',
        required=True,
        index=True
    )

    # Cumulative counters
    bytes_sent_total = fields.Float(string='Total Bytes Sent', digits=(20, 0))
    bytes_recv_total = fields.Float(string='Total Bytes Received', digits=(20, 0))
    packets_sent = fields.Float(string='Packets Sent', digits=(20, 0))
    packets_recv = fields.Float(string='Packets Received', digits=(20, 0))
    errors_in = fields.Integer(string='Incoming Errors')
    errors_out = fields.Integer(string='Outgoing Errors')

    # Calculated throughput (MB/s)
    speed_send_mbps = fields.Float(string='Upload Speed (MB/s)', digits=(10, 3))
    speed_recv_mbps = fields.Float(string='Download Speed (MB/s)', digits=(10, 3))

    # Display fields
    bytes_sent_mb = fields.Float(
        string='Sent (MB)',
        compute='_compute_mb',
        store=False
    )
    bytes_recv_mb = fields.Float(
        string='Received (MB)',
        compute='_compute_mb',
        store=False
    )


    @api.depends('bytes_sent_total', 'bytes_recv_total')
    def _compute_mb(self):
        for rec in self:
            rec.bytes_sent_mb = rec.bytes_sent_total / 1024**2
            rec.bytes_recv_mb = rec.bytes_recv_total / 1024**2

    @api.model
    def get_network_history(self, interface=None, period='24h'):
        """Retourne l'historique réseau pour les graphes"""
        from datetime import datetime, timedelta
        now = fields.Datetime.now()

        period_map = {'24h': 24, '7d': 168, '30d': 720}
        hours = period_map.get(period, 24)
        since = now - timedelta(hours=hours)

        domain = [('timestamp', '>=', since)]
        if interface:
            domain.append(('interface', '=', interface))

        records = self.search(domain, order='timestamp asc')
        return [{
            'timestamp': r.timestamp.isoformat(),
            'interface': r.interface,
            'speed_send': r.speed_send_mbps,
            'speed_recv': r.speed_recv_mbps,
        } for r in records]

    @api.model
    def get_available_interfaces(self):
        """Retourne la liste des interfaces disponibles"""
        interfaces = self.search([]).mapped('interface')
        return list(set(interfaces))
