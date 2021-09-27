# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ServerMonitoring(models.Model):
    
    _name = 'server.monitoring'
    _description = 'Server Monitoring'


    name = fields.Char('name')
    