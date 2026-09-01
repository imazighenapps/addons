# -*- coding: utf-8 -*-
from odoo import fields, models

class EduflowTimeSlot(models.Model):
    _name = 'eduflow.time.slot'
    _description = "Time Slot"
    _order = 'sequence, hour_from'

    name = fields.Char(string="Slot Name", required=True)
    sequence = fields.Integer(default=10)
    hour_from = fields.Float(string="From", required=True)
    hour_to = fields.Float(string="To", required=True)
    is_break = fields.Boolean(string="Is Break", default=False)
    company_id = fields.Many2one('res.company', string="Institution", default=lambda self: self.env.company)
    active = fields.Boolean(default=True)
