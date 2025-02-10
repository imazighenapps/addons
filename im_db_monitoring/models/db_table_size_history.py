from odoo import models, fields


class DBTableSizeHistory(models.Model):
    _name = 'db.table.size.history'
    _description = 'History of table sizes'
    
    date_from               = fields.Datetime(string="Date from")
    date_to                 = fields.Datetime(string="Date to")
    table_name              = fields.Char(string="Table name")
    total_size              = fields.Char(string="Total size")
    total_size_bytes        = fields.Integer(string="Total size in bytes")
    status                  = fields.Selection([('draft', 'Draft'),('valid', 'Valid')], string='Status')
