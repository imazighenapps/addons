from odoo import models, fields



class DBTuplesInOutHistory(models.Model):
    _name = 'db.tuples.history'
    _description = 'History of inserted, updated, and deleted tuples'
    
    date_from               = fields.Datetime(string="Date from")
    date_to                 = fields.Datetime(string="Date to")
    inserts = fields.Integer(string="Inserts")
    updates = fields.Integer(string="Updates")
    deletes = fields.Integer(string="Deletes")
    status                  = fields.Selection([('draft', 'Draft'),('valid', 'Valid')], string='Status')
