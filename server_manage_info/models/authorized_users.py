# -*- coding: utf-8 -*-
from odoo import api, fields, models


class AuthorizedUsers(models.Model):

    _name = 'authorized.users'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _description = 'utilisateurs autorisés'


    mane = fields.Char(
        string='field_name',
    )
    
   