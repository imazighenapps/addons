# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import json
import psutil
import logging
_logger = logging.getLogger(__name__)


class ServerMonitorController(http.Controller):

    @http.route('/server_monitor/dashboard_data', type='jsonrpc', auth='user', methods=['POST'])
    def get_dashboard_data(self, **kwargs):
        """Endpoint principal du dashboard"""
        try:
            data = request.env['server.monitor.config'].get_dashboard_data()
            return data
        except Exception as e:
            _logger.error(f"Erreur dashboard data : {e}", exc_info=True)
            return {'error': str(e)}

    @http.route('/server_monitor/history', type='jsonrpc', auth='user', methods=['POST'])
    def get_history(self, period='24h', **kwargs):
        """Retourne l'historique des métriques"""
        try:
            data = request.env['server.monitor.history'].get_history_data(period=period)
            return {'data': data}
        except Exception as e:
            return {'error': str(e)}

    @http.route('/server_monitor/network_history', type='jsonrpc', auth='user', methods=['POST'])
    def get_network_history(self, interface=None, period='24h', **kwargs):
        """Retourne l'historique réseau"""
        try:
            data = request.env['server.monitor.network'].get_network_history(
                interface=interface,
                period=period
            )
            return {'data': data}
        except Exception as e:
            return {'error': str(e)}

    @http.route('/server_monitor/processes', type='jsonrpc', auth='user', methods=['POST'])
    def get_processes(self, **kwargs):
        """Retourne les processus en cours"""
        try:
            data = request.env['server.monitor.process'].get_top_processes_data(limit=50)
            return {'processes': data}
        except Exception as e:
            return {'error': str(e)}

    @http.route('/server_monitor/kill_process', type='jsonrpc', auth='user', methods=['POST'])
    def kill_process(self, pid=None, name=None, **kwargs):
        """Endpoint pour tuer un processus (admin uniquement)"""
        try:
            if not request.env.user.has_group('im_server_monitoring_pro.group_server_monitor_admin'):
                return {'error': 'Permission refusée. Droits administrateur requis.'}

            if not pid:
                return {'error': 'PID requis'}

            # Trouver et terminer le processus
            proc = psutil.Process(int(pid))
            proc_name = proc.name()

            protected = ['systemd', 'init', 'kthreadd', 'odoo', 'python', 'postgres']
            if proc_name.lower() in protected or int(pid) <= 100:
                return {'error': f"Processus protégé : {proc_name}"}

            proc.terminate()

            _logger.warning(
                f"Processus tué via dashboard par {request.env.user.name}: "
                f"PID={pid}, Nom={proc_name}"
            )
            return {'success': True, 'message': f"Processus {proc_name} (PID: {pid}) terminé."}
        except psutil.NoSuchProcess:
            return {'error': f'Le processus PID {pid} n\'existe plus.'}
        except psutil.AccessDenied:
            return {'error': 'Permission refusée par le système d\'exploitation.'}
        except Exception as e:
            return {'error': str(e)}

    @http.route('/server_monitor/acknowledge_alert', type='jsonrpc', auth='user', methods=['POST'])
    def acknowledge_alert(self, alert_id=None, **kwargs):
        """Acquitte une alerte"""
        try:
            if not alert_id:
                return {'error': 'alert_id requis'}
            alert = request.env['server.monitor.alert'].browse(int(alert_id))
            alert.action_acknowledge()
            return {'success': True}
        except Exception as e:
            return {'error': str(e)}
