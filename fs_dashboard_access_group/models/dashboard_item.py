# -*- coding: utf-8 -*-


import logging
from odoo import models, fields, api
_logger = logging.getLogger(__name__)



class DashboardItem(models.Model):
    _inherit = 'dashboard.item'
    
    user_ids = fields.Many2many(comodel_name='res.users',string='Users') 
