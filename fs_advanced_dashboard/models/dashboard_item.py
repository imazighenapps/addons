# -*- coding: utf-8 -*-

from odoo import models, fields, api



class DashboardItem(models.Model):
    _inherit = 'dashboard.item'
    

    objective     = fields.Selection([('increase', 'Increase'),('decrease', 'decrease')], string="Objective", default="increase")
   