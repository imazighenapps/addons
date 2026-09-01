# -*- coding: utf-8 -*-
from odoo import fields, models

class EduflowTeacherAvailability(models.Model):
    _name = 'eduflow.teacher.availability'
    _description = "Teacher Availability"
    _order = 'teacher_id, day, hour_from'

    teacher_id = fields.Many2one('eduflow.teacher', string="Teacher", required=True, ondelete='cascade')
    day = fields.Selection([
        ('0', 'Monday'), ('1', 'Tuesday'), ('2', 'Wednesday'),
        ('3', 'Thursday'), ('4', 'Friday'), ('5', 'Saturday'), ('6', 'Sunday'),
    ], string="Day", required=True)
    hour_from = fields.Float(string="From", required=True)
    hour_to = fields.Float(string="To", required=True)
    preference = fields.Selection([('1','Preferred'),('2','Normal'),('3','Avoid')], string="Preference", default='2')
    available = fields.Boolean(string="Available", default=True)
    company_id = fields.Many2one('res.company', string="Institution", default=lambda self: self.env.company)
