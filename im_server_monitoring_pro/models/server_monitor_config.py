# -*- coding: utf-8 -*-
import logging
import psutil
import os
import platform
from datetime import datetime, timedelta
from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class ServerMonitorConfig(models.Model):
    _name = 'server.monitor.config'
    _description = 'Server Monitoring Configuration'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    name = fields.Char(string='Name', required=True, default='Main Configuration')
    active = fields.Boolean(default=True)

    # === CPU THRESHOLDS ===
    cpu_warning_threshold = fields.Float(
        string='CPU Warning Threshold (%)',
        default=70.0,
        help='Percentage threshold that triggers a CPU warning alert'
    )
    cpu_critical_threshold = fields.Float(
        string='CPU Critical Threshold (%)',
        default=90.0,
        help='Percentage threshold that triggers a CPU critical alert'
    )

    # === RAM THRESHOLDS ===
    ram_warning_threshold = fields.Float(
        string='RAM Warning Threshold (%)',
        default=75.0,
        help='Percentage threshold that triggers a RAM warning alert'
    )
    ram_critical_threshold = fields.Float(
        string='RAM Critical Threshold (%)',
        default=90.0,
        help='Percentage threshold that triggers a RAM critical alert'
    )

    # === DISK THRESHOLDS ===
    disk_warning_threshold = fields.Float(
        string='Disk Warning Threshold (%)',
        default=80.0,
        help='Percentage threshold that triggers a Disk warning alert'
    )
    disk_critical_threshold = fields.Float(
        string='Disk Critical Threshold (%)',
        default=95.0,
        help='Percentage threshold that triggers a Disk critical alert'
    )

    # === NETWORK THRESHOLDS ===
    network_warning_threshold = fields.Float(
        string='Network Warning Threshold (MB/s)',
        default=50.0,
        help='Throughput in MB/s that triggers a network warning alert'
    )
    network_critical_threshold = fields.Float(
        string='Network Critical Threshold (MB/s)',
        default=90.0,
        help='Throughput in MB/s that triggers a network critical alert'
    )

    # === NOTIFICATIONS ===
    enable_email_alerts = fields.Boolean(
        string='Enable Email Alerts',
        default=True
    )
    alert_email_ids = fields.Many2many(
        'res.partner',
        string='Email Alert Recipients',
        help='Partners who will receive alert emails'
    )
    enable_odoo_notifications = fields.Boolean(
        string='Enable Odoo Notifications',
        default=True
    )
    alert_user_ids = fields.Many2many(
        'res.users',
        string='Users to Notify',
        help='Users who will receive Odoo notifications'
    )

    # === COLLECTION SETTINGS ===
    collection_interval = fields.Selection([
        ('30', '30 Seconds'),
        ('60', '1 Minute'),
        ('300', '5 Minutes'),
        ('600', '10 Minutes'),
    ], string='Collection Interval', default='60')

    history_retention_days = fields.Integer(
        string='History Retention (Days)',
        default=30,
        help='Number of days to keep historical monitoring data'
    )

    # === CURRENT STATUS (Computed) ===
    current_cpu_percent = fields.Float(
        string='Current CPU (%)',
        compute='_compute_current_stats',
        store=False
    )
    current_ram_percent = fields.Float(
        string='Current RAM (%)',
        compute='_compute_current_stats',
        store=False
    )
    current_disk_percent = fields.Float(
        string='Current Disk (%)',
        compute='_compute_current_stats',
        store=False
    )

    cpu_status = fields.Char(
        string='CPU Status',
        compute='_compute_status_colors',
        store=False
    )
    ram_status = fields.Char(
        string='RAM Status',
        compute='_compute_status_colors',
        store=False
    )
    disk_status = fields.Char(
        string='Disk Status',
        compute='_compute_status_colors',
        store=False
    )

    last_collection = fields.Datetime(
        string='Last Collection',
        readonly=True
    )


    @api.depends()
    def _compute_current_stats(self):
        for record in self:
            try:
                record.current_cpu_percent = psutil.cpu_percent(interval=0.1)
                mem = psutil.virtual_memory()
                record.current_ram_percent = mem.percent
                disk = psutil.disk_usage('/')
                record.current_disk_percent = disk.percent
            except Exception as e:
                _logger.warning(f"Impossible de lire les stats système : {e}")
                record.current_cpu_percent = 0.0
                record.current_ram_percent = 0.0
                record.current_disk_percent = 0.0

    @api.depends('current_cpu_percent', 'current_ram_percent', 'current_disk_percent',
                 'cpu_warning_threshold', 'cpu_critical_threshold',
                 'ram_warning_threshold', 'ram_critical_threshold',
                 'disk_warning_threshold', 'disk_critical_threshold')
    def _compute_status_colors(self):
        for record in self:
            record.cpu_status = self._get_status(
                record.current_cpu_percent,
                record.cpu_warning_threshold,
                record.cpu_critical_threshold
            )
            record.ram_status = self._get_status(
                record.current_ram_percent,
                record.ram_warning_threshold,
                record.ram_critical_threshold
            )
            record.disk_status = self._get_status(
                record.current_disk_percent,
                record.disk_warning_threshold,
                record.disk_critical_threshold
            )

    def _get_status(self, value, warning, critical):
        if value >= critical:
            return 'danger'
        elif value >= warning:
            return 'warning'
        return 'success'

    def action_collect_now(self):
        """Immediate metrics collection"""
        self.ensure_one()
        self._collect_metrics()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Collection completed'),
                'message': _('Metrics have been successfully collected.'),
                'type': 'success',
                'sticky': False,
            }
        }

    def action_open_dashboard(self):
        return {
            'type': 'ir.actions.client',
            'tag': 'server_monitor_dashboard',
        }

    def action_cleanup_history(self):
        """Delete old history records"""
        self.ensure_one()
        cutoff = datetime.now() - timedelta(days=self.history_retention_days)
        old_records = self.env['server.monitor.history'].search([
            ('timestamp', '<', cutoff)
        ])
        count = len(old_records)
        old_records.unlink()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Cleanup completed'),
                'message': _(f'{count} records deleted.'),
                'type': 'success',
            }
        }

    @api.model
    def _collect_metrics(self):
        """Méthode principale de collecte - appelée par le cron"""
        config = self.search([], limit=1)
        if not config:
            return

        try:
            # --- CPU ---
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_freq = psutil.cpu_freq()
            cpu_count = psutil.cpu_count()
            cpu_count_logical = psutil.cpu_count(logical=True)

            # --- RAM ---
            mem = psutil.virtual_memory()
            swap = psutil.swap_memory()

            # --- DISQUES ---
            disk_partitions = psutil.disk_partitions()
            disk_data = []
            for partition in disk_partitions:
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disk_data.append({
                        'device': partition.device,
                        'mountpoint': partition.mountpoint,
                        'fstype': partition.fstype,
                        'total': usage.total,
                        'used': usage.used,
                        'free': usage.free,
                        'percent': usage.percent,
                    })
                except PermissionError:
                    continue

            # --- RÉSEAU ---
            net_io = psutil.net_io_counters(pernic=True)
            net_data = []
            for iface, counters in net_io.items():
                net_data.append({
                    'interface': iface,
                    'bytes_sent': counters.bytes_sent,
                    'bytes_recv': counters.bytes_recv,
                    'packets_sent': counters.packets_sent,
                    'packets_recv': counters.packets_recv,
                    'errin': counters.errin,
                    'errout': counters.errout,
                })

            # Créer l'enregistrement d'historique
            history = self.env['server.monitor.history'].create({
                'config_id': config.id,
                'timestamp': fields.Datetime.now(),
                # CPU
                'cpu_percent': cpu_percent,
                'cpu_freq_current': cpu_freq.current if cpu_freq else 0,
                'cpu_freq_max': cpu_freq.max if cpu_freq else 0,
                'cpu_count_physical': cpu_count or 0,
                'cpu_count_logical': cpu_count_logical or 0,
                # RAM
                'ram_total': mem.total,
                'ram_used': mem.used,
                'ram_available': mem.available,
                'ram_percent': mem.percent,
                'swap_total': swap.total,
                'swap_used': swap.used,
                'swap_percent': swap.percent,
                # Disque (partition principale)
                'disk_total': disk_data[0]['total'] if disk_data else 0,
                'disk_used': disk_data[0]['used'] if disk_data else 0,
                'disk_free': disk_data[0]['free'] if disk_data else 0,
                'disk_percent': disk_data[0]['percent'] if disk_data else 0,
            })

            # Enregistrer les données réseau
            for net in net_data:
                # Chercher le dernier enregistrement pour calculer le débit
                last_net = self.env['server.monitor.network'].search([
                    ('interface', '=', net['interface']),
                ], order='timestamp desc', limit=1)

                speed_send = 0.0
                speed_recv = 0.0
                if last_net:
                    time_delta = (datetime.now() - last_net.timestamp).total_seconds()
                    if time_delta > 0:
                        speed_send = (net['bytes_sent'] - last_net.bytes_sent_total) / time_delta / 1024 / 1024
                        speed_recv = (net['bytes_recv'] - last_net.bytes_recv_total) / time_delta / 1024 / 1024
                        speed_send = max(0, speed_send)
                        speed_recv = max(0, speed_recv)

                self.env['server.monitor.network'].create({
                    'history_id': history.id,
                    'timestamp': fields.Datetime.now(),
                    'interface': net['interface'],
                    'bytes_sent_total': net['bytes_sent'],
                    'bytes_recv_total': net['bytes_recv'],
                    'packets_sent': net['packets_sent'],
                    'packets_recv': net['packets_recv'],
                    'errors_in': net['errin'],
                    'errors_out': net['errout'],
                    'speed_send_mbps': speed_send,
                    'speed_recv_mbps': speed_recv,
                })

            # Mettre à jour la date de dernière collecte
            config.write({'last_collection': fields.Datetime.now()})

            # Vérifier les alertes
            config._check_alerts(history)

            # Nettoyage automatique
            config._auto_cleanup()

        except Exception as e:
            _logger.error(f"Erreur lors de la collecte des métriques : {e}", exc_info=True)

    def _check_alerts(self, history):
        """Check thresholds and create alerts if necessary"""
        self.ensure_one()

        checks = [
            {
                'metric': 'cpu',
                'value': history.cpu_percent,
                'warning': self.cpu_warning_threshold,
                'critical': self.cpu_critical_threshold,
                'label': 'CPU',
                'unit': '%',
            },
            {
                'metric': 'ram',
                'value': history.ram_percent,
                'warning': self.ram_warning_threshold,
                'critical': self.ram_critical_threshold,
                'label': 'RAM',
                'unit': '%',
            },
            {
                'metric': 'disk',
                'value': history.disk_percent,
                'warning': self.disk_warning_threshold,
                'critical': self.disk_critical_threshold,
                'label': 'Disk',
                'unit': '%',
            },
        ]

        for check in checks:
            if check['value'] >= check['critical']:
                severity = 'critical'
            elif check['value'] >= check['warning']:
                severity = 'warning'
            else:
                continue

            # Avoid duplicate alerts within 5 minutes
            recent_alert = self.env['server.monitor.alert'].search([
                ('metric_type', '=', check['metric']),
                ('severity', '=', severity),
                ('state', '=', 'open'),
                ('create_date', '>=', fields.Datetime.now() - timedelta(minutes=5)),
            ], limit=1)

            if not recent_alert:
                self.env['server.monitor.alert'].create({
                    'config_id': self.id,
                    'history_id': history.id,
                    'metric_type': check['metric'],
                    'severity': severity,
                    'value': check['value'],
                    'threshold': check['critical'] if severity == 'critical' else check['warning'],
                    'message': _(
                        f"⚠️ {check['label']} : {check['value']:.1f}{check['unit']} "
                        f"exceeds the {'critical' if severity == 'critical' else 'warning'} "
                        f"threshold of {check['critical'] if severity == 'critical' else check['warning']:.1f}{check['unit']}"
                    ),
                })

    def _auto_cleanup(self):
        """Nettoyage automatique des anciens enregistrements"""
        cutoff = datetime.now() - timedelta(days=self.history_retention_days)
        self.env['server.monitor.history'].search([('timestamp', '<', cutoff)]).unlink()

    @api.model
    def get_dashboard_data(self):
        """Return all data for the JS dashboard"""
        config = self.search([], limit=1)
        if not config:
            return {'error': 'No configuration found'}

        try:
            # Stats temps réel
            cpu_percent = psutil.cpu_percent(interval=0.1)
            cpu_count_logical = psutil.cpu_count(logical=True)
            mem = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            net_io = psutil.net_io_counters(pernic=True)

            # CPU par core
            cpu_per_core = psutil.cpu_percent(percpu=True, interval=0.1)

            # Infos système
            boot_time = psutil.boot_time()
            uptime = datetime.now() - datetime.fromtimestamp(boot_time)

            # Top processus
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status', 'username']):
                try:
                    pinfo = proc.info
                    pinfo['memory_mb'] = proc.memory_info().rss / 1024 / 1024
                    processes.append(pinfo)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            processes.sort(key=lambda x: x.get('cpu_percent', 0), reverse=True)
            top_processes = processes[:20]

            # Interfaces réseau
            net_interfaces = []
            for iface, counters in net_io.items():
                last_net = self.env['server.monitor.network'].search([
                    ('interface', '=', iface),
                ], order='timestamp desc', limit=1)
                net_interfaces.append({
                    'interface': iface,
                    'bytes_sent': counters.bytes_sent,
                    'bytes_recv': counters.bytes_recv,
                    'speed_send': last_net.speed_send_mbps if last_net else 0,
                    'speed_recv': last_net.speed_recv_mbps if last_net else 0,
                })

            # Partitions disque
            disk_partitions = []
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disk_partitions.append({
                        'device': partition.device,
                        'mountpoint': partition.mountpoint,
                        'total_gb': usage.total / 1024**3,
                        'used_gb': usage.used / 1024**3,
                        'free_gb': usage.free / 1024**3,
                        'percent': usage.percent,
                    })
                except PermissionError:
                    continue

            # Historique (dernières 24h)
            since_24h = fields.Datetime.now() - timedelta(hours=24)
            history_records = self.env['server.monitor.history'].search([
                ('timestamp', '>=', since_24h),
            ], order='timestamp asc')

            history_data = [{
                'timestamp': r.timestamp.isoformat(),
                'cpu': r.cpu_percent,
                'ram': r.ram_percent,
                'disk': r.disk_percent,
            } for r in history_records]

            # Alertes ouvertes
            open_alerts = self.env['server.monitor.alert'].search([
                ('state', '=', 'open'),
            ], order='create_date desc', limit=10)
            alerts_data = [{
                'id': a.id,
                'metric': a.metric_type,
                'severity': a.severity,
                'message': a.message,
                'value': a.value,
                'date': a.create_date.isoformat(),
            } for a in open_alerts]

            return {
                'realtime': {
                    'cpu_percent': cpu_percent,
                    'cpu_count_logical': cpu_count_logical,
                    'cpu_per_core': cpu_per_core,
                    'ram_percent': mem.percent,
                    'ram_used_gb': mem.used / 1024**3,
                    'ram_total_gb': mem.total / 1024**3,
                    'ram_available_gb': mem.available / 1024**3,
                    'disk_percent': disk.percent,
                    'disk_used_gb': disk.used / 1024**3,
                    'disk_total_gb': disk.total / 1024**3,
                    'disk_free_gb': disk.free / 1024**3,
                    'uptime_days': uptime.days,
                    'uptime_hours': uptime.seconds // 3600,
                    'uptime_minutes': (uptime.seconds % 3600) // 60,
                    'platform': platform.system(),
                    'hostname': platform.node(),
                },
                'cpu_status': config._get_status(cpu_percent, config.cpu_warning_threshold, config.cpu_critical_threshold),
                'ram_status': config._get_status(mem.percent, config.ram_warning_threshold, config.ram_critical_threshold),
                'disk_status': config._get_status(disk.percent, config.disk_warning_threshold, config.disk_critical_threshold),
                'thresholds': {
                    'cpu_warning': config.cpu_warning_threshold,
                    'cpu_critical': config.cpu_critical_threshold,
                    'ram_warning': config.ram_warning_threshold,
                    'ram_critical': config.ram_critical_threshold,
                    'disk_warning': config.disk_warning_threshold,
                    'disk_critical': config.disk_critical_threshold,
                },
                'net_interfaces': net_interfaces,
                'disk_partitions': disk_partitions,
                'top_processes': top_processes,
                'history': history_data,
                'alerts': alerts_data,
                'last_collection': config.last_collection.isoformat() if config.last_collection else None,
            }
        except Exception as e:
            _logger.error(f"Erreur get_dashboard_data : {e}", exc_info=True)
            return {'error': str(e)}
