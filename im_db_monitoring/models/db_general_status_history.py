from odoo import models, fields

class DBGeneralStatusHistory(models.Model):
    _name = 'db.general.status.history'
    _description = 'History of general database status'
    
    date_from           = fields.Datetime(string="Date from")
    date_to             = fields.Datetime(string="Date to")
    table_count         = fields.Integer(string="Number of tables")
    db_size             = fields.Float(string="Database size (MB)")
    postgres_version    = fields.Char(string="PostgreSQL version")
    view_count          = fields.Integer(string="Number of views")
    active_connections  = fields.Integer(string="Active connections")
    pending_locks       = fields.Integer(string="Pending locks")
    status                  = fields.Selection([('draft', 'Draft'),('valid', 'Valid')], string='Status')
