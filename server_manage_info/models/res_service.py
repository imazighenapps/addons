# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ResService(models.Model):
    _name = 'res.service'
    _description = 'service'

    name        = fields.Char(string='Nom de service')
    port        = fields.Char(string='Port') 
