from odoo import models, fields







class Holiday(models.Model):
    _name = 'appointment.holiday'
    _description = 'Holiday'

    name = fields.Char(string='Name', required=True)
    date_from = fields.Date(string='From', required=True)
    date_to = fields.Date(string='To', required=True)
    calendar_id = fields.Many2one('appointment.calendar', string='Calendar')
