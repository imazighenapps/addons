# -*- coding: utf-8 -*-
from odoo import api, fields, models
import string
import random
import logging
_logger = logging.getLogger(__name__)

class OdooUsers(models.Model):
    _name = 'server.users'
    _inherit = ['mail.thread', 'mail.activity.mixin',]
    _description = 'utilisateurs serveur'

    name           = fields.Char(string="Login", required=False)  
    password        = fields.Char(string='Password', required=False) 
    port            = fields.Char(string='Port')   
    server_id       = fields.Many2one(string='Serveur',comodel_name='res.server')
    service_id      = fields.Many2one(string="Service",comodel_name='res.service', required=False)      
    password_length = fields.Integer(string='Password length',defaullt=8) 
    
    def generate_random_password(self):
        length = 8
        characters = list(string.ascii_letters + string.digits + "!@#$%^&*()")
        if self.password_length > 0 :
             length = self.password_length
        random.shuffle(characters)
        password = []
        for i in range(length):
            password.append(random.choice(characters))
        random.shuffle(password)
        password =  ("".join(password))
        self.password = password
        _logger.warning('\n ok ok password=>%s',password)


   
    @api.onchange('service_id')
    def validate_form(self):
       self.port = self.service_id.port