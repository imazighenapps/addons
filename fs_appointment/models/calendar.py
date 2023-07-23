from odoo import models, fields





class Calendar(models.Model):
    _name = 'appointment.calendar'
    _description = 'Calendar'

    name = fields.Char(string='Name', required=True)
  
  
    opening_hour    = fields.Float(string='Opening Hour')
    closing_hour    = fields.Float(string='Closing Hour')

    monday          = fields.Boolean(string='Monday', default='True')
    tuesday         = fields.Boolean(string='Tuesday', default='True')
    wednesday       = fields.Boolean(string='Wednesday', default='True')
    thursday        = fields.Boolean(string='Thursday', default='True')
    friday          = fields.Boolean(string='Friday', default='True')
    saturday        = fields.Boolean(string='Saturday', default='True')
    sunday          = fields.Boolean(string='Sunday', default='True')
    holiday_ids     = fields.One2many('appointment.holiday', 'calendar_id' ,string='Holidays')





