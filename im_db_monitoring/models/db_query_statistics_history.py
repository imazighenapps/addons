from odoo import models, fields

class DBQueryStatisticsHistory(models.Model):
    _name = 'db.query.statistics.history'
    _description = 'History of executed query statistics'
    

    
    date_from               = fields.Datetime(string="Date from")
    date_to                 = fields.Datetime(string="Date to")
    total_commits           = fields.Integer(string="Total commits")
    total_rollbacks         = fields.Integer(string="Total rollbacks")
    total_rows_read         = fields.Integer(string="Total rows read")
    total_rows_modified     = fields.Integer(string="Total rows modified")
    total_blocks_accessed   = fields.Integer(string="Total blocks accessed")
    status                  = fields.Selection([('draft', 'Draft'),('valid', 'Valid')], string='Status')


