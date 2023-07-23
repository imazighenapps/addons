from odoo import models, fields






class Notification(models.Model):
    _name = 'appointment.notification'
    _description = 'Notification'

    name = fields.Char(string='Name', required=True)
    method = fields.Selection([('email', 'Email'), ('sms', 'SMS')], string='Method')
    time = fields.Float(string='Time')
    appointment_id = fields.Many2one('appointment.appointment', string='Appointment')
