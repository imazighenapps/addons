import datetime
from odoo import fields, http, SUPERUSER_ID, tools, _
from odoo.http import request
import time
import psutil
import logging
_logger = logging.getLogger(__name__)


class Servermonitoring(http.Controller):

    
    @http.route('/server/monitoring/cpu/informations', type='json', auth='user')
    def get_cpu_informations(self,**k):
        cpu_percent = psutil.cpu_percent(interval=0.1)
        current_seconds = fields.datetime.now().strftime("%S")
       
        return {'cpu_percent':cpu_percent,
                'current_seconds':current_seconds,
                'cpu_count_logical' : psutil.cpu_count(logical=True),
                'cpu_count_phisical' : psutil.cpu_count(logical=False),

                }
        
    @http.route('/server/monitoring/ram/informations', type='json', auth='user')
    def get_ram_informations(self,**k):
        current_seconds = fields.datetime.now().strftime("%S")
        ram_percent = psutil.virtual_memory()
        percent_used = ram_percent.used * 100 / ram_percent.total 
        return {'percent_used':"{:.2f}".format(percent_used),
                'percent_free':100.0 - float("{:.2f}".format(percent_used)),
                'total':"{:.2f}".format(ram_percent.total/1073741824),
                'used':"{:.2f}".format(ram_percent.used/1073741824),
                'free':"{:.2f}".format((ram_percent.total/1073741824) - (ram_percent.used/1073741824)),
                'current_seconds':current_seconds,

                }

    @http.route('/server/net/available_networks', type='json', auth='user')
    def get_net_available_networks(self,**k):
        addresses = psutil.net_if_addrs()
        stats = psutil.net_if_stats()
        available_networks = []
        for intface, addr_list in addresses.items():
            if any(getattr(addr, 'address').startswith("169.254") for addr in addr_list):
                continue
            elif intface in stats and getattr(stats[intface], "isup"):
                available_networks.append(intface)          
        if 'lo' in available_networks:
            available_networks.remove('lo')
        return available_networks
       
    @http.route('/server/net/informations', type='json', auth='user')
    def get_networks_informations(self,**k):
        natwork_name = k.get('data').get('natwork_name')
        current_seconds = fields.datetime.now().strftime("%S")
        net_stat = psutil.net_io_counters(pernic=True)[natwork_name]
        net_in = round(net_stat.bytes_recv/ 1024/1024*8 , 1)
        net_out = round(net_stat.bytes_sent / 1024/1024*8, 1)
        speed = psutil.net_if_stats().get(natwork_name).speed
        
        return {
                'net_in' : net_in,
                'net_out' : net_out,
                'current_seconds':current_seconds,
                'speed':speed    
                }
       




