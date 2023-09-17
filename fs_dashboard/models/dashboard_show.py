# -*- coding: utf-8 -*-


import logging
from odoo import models, fields, api
_logger = logging.getLogger(__name__)




class DashboardShow(models.Model):
    _name = 'dashboard.show'
    _description = 'Dashboard show'

    name = fields.Char(string="Name")


    # @api.model
    # def get_dashboard_data(self, sections=None):
    #     return [1,2,3,4]
    