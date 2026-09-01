# -*- coding: utf-8 -*-
from odoo import fields, models


class EduflowAcademicPeriod(models.Model):
    _name = 'eduflow.academic.period'
    _description = "Academic Period (trimester / semester)"
    _order = 'year_id, sequence, date_start'

    name = fields.Char(string="Period", required=True, help="Ex: Trimester 1")
    year_id = fields.Many2one('eduflow.academic.year', string="Academic Year",
                               required=True, ondelete='cascade')
    date_start = fields.Date(string="Start Date", required=True)
    date_end = fields.Date(string="End Date", required=True)
    sequence = fields.Integer(string="Sequence", default=10)
    type = fields.Selection([
        ('trimester', 'Trimester'),
        ('semester', 'Semester'),
        ('custom', 'Custom'),
    ], string="Type", default='trimester', required=True)
