from odoo import models, fields



class DBTuplesFetchedReturnedHistory(models.Model):
    _name = 'db.tuples.fetched.returned.history'
    _description = 'History of tuples fetched via index and sequential scans'
    
    date_from               = fields.Datetime(string="Date from")
    date_to                 = fields.Datetime(string="Date to")
    fetched = fields.Integer(string="Tuples fetched via index")
    returned = fields.Integer(string="Tuples returned via sequential scan")
    status                  = fields.Selection([('draft', 'Draft'),('valid', 'Valid')], string='Status')
