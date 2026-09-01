# -*- coding: utf-8 -*-
from odoo import fields, models

class EduflowRoom(models.Model):
    _name = 'eduflow.room'
    _description = "Classroom / Room"
    _order = 'name'

    name = fields.Char(string="Room Name", required=True)
    code = fields.Char(string="Code")
    capacity = fields.Integer(string="Capacity", default=30)
    room_type = fields.Selection([
        ('classroom', 'Classroom'),
        ('lab', 'Laboratory'),
        ('gym', 'Gym'),
        ('other', 'Other'),
    ], string="Room Type", default='classroom', required=True)
    company_id = fields.Many2one('res.company', string="Institution", default=lambda self: self.env.company)
    active = fields.Boolean(default=True)
    notes = fields.Text(string="Notes")
