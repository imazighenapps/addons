from odoo import models, fields




class DBBlockIOHistory(models.Model):
    _name = 'db.block.io.history'
    _description = 'History of block I/O operations'
    
    date_from               = fields.Datetime(string="Date from")
    date_to                 = fields.Datetime(string="Date to")
    reads                   = fields.Integer(string="Blocks read")
    hits                    = fields.Integer(string="Blocks found in cache")
    status                  = fields.Selection([('draft', 'Draft'),('valid', 'Valid')], string='Status')
