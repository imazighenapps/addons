# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ServerMonitorHistory(models.Model):
    _name = 'server.monitor.history'
    _description = 'Server Metrics History'
    _order = 'timestamp desc'
    _rec_name = 'timestamp'

    config_id = fields.Many2one(
        'server.monitor.config',
        string='Configuration',
        required=True,
        ondelete='cascade'
    )

    timestamp = fields.Datetime(
        string='Timestamp',
        required=True,
        default=fields.Datetime.now,
        index=True
    )

    # === CPU ===
    cpu_percent = fields.Float(string='CPU (%)', digits=(5, 2))
    cpu_freq_current = fields.Float(string='Current CPU Frequency (MHz)', digits=(10, 2))
    cpu_freq_max = fields.Float(string='Max CPU Frequency (MHz)', digits=(10, 2))
    cpu_count_physical = fields.Integer(string='Physical Cores')
    cpu_count_logical = fields.Integer(string='Logical Cores')

    # === RAM ===
    ram_total = fields.Float(string='Total RAM (bytes)', digits=(20, 0))
    ram_used = fields.Float(string='Used RAM (bytes)', digits=(20, 0))
    ram_available = fields.Float(string='Available RAM (bytes)', digits=(20, 0))
    ram_percent = fields.Float(string='RAM (%)', digits=(5, 2))
    swap_total = fields.Float(string='Total Swap (bytes)', digits=(20, 0))
    swap_used = fields.Float(string='Used Swap (bytes)', digits=(20, 0))
    swap_percent = fields.Float(string='Swap (%)', digits=(5, 2))

    # === DISK ===
    disk_total = fields.Float(string='Total Disk (bytes)', digits=(20, 0))
    disk_used = fields.Float(string='Used Disk (bytes)', digits=(20, 0))
    disk_free = fields.Float(string='Free Disk (bytes)', digits=(20, 0))
    disk_percent = fields.Float(string='Disk (%)', digits=(5, 2))

    # === COMPUTED DISPLAY FIELDS ===
    ram_total_gb = fields.Float(
        string='Total RAM (GB)',
        compute='_compute_gb_fields',
        store=False
    )
    ram_used_gb = fields.Float(
        string='Used RAM (GB)',
        compute='_compute_gb_fields',
        store=False
    )
    disk_total_gb = fields.Float(
        string='Total Disk (GB)',
        compute='_compute_gb_fields',
        store=False
    )
    disk_used_gb = fields.Float(
        string='Used Disk (GB)',
        compute='_compute_gb_fields',
        store=False
    )
    disk_free_gb = fields.Float(
        string='Free Disk (GB)',
        compute='_compute_gb_fields',
        store=False
    )

    network_ids = fields.One2many(
        'server.monitor.network',
        'history_id',
        string='Network Interfaces'
    )


    @api.depends('ram_total', 'ram_used', 'disk_total', 'disk_used', 'disk_free')
    def _compute_gb_fields(self):
        for record in self:
            record.ram_total_gb = record.ram_total / 1024**3
            record.ram_used_gb = record.ram_used / 1024**3
            record.disk_total_gb = record.disk_total / 1024**3
            record.disk_used_gb = record.disk_used / 1024**3
            record.disk_free_gb = record.disk_free / 1024**3

    @api.model
    def get_history_data(self, period='24h'):
        """Retourne les données d'historique pour les graphes"""
        from datetime import datetime, timedelta
        now = fields.Datetime.now()

        if period == '24h':
            since = now - timedelta(hours=24)
        elif period == '7d':
            since = now - timedelta(days=7)
        elif period == '30d':
            since = now - timedelta(days=30)
        else:
            since = now - timedelta(hours=24)

        records = self.search([
            ('timestamp', '>=', since),
        ], order='timestamp asc')

        return [{
            'timestamp': r.timestamp.isoformat(),
            'cpu': r.cpu_percent,
            'ram': r.ram_percent,
            'disk': r.disk_percent,
            'swap': r.swap_percent,
        } for r in records]
