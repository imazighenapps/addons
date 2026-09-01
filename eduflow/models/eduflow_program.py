# -*- coding: utf-8 -*-
from odoo import fields, models


class EduflowProgram(models.Model):
    _name = 'eduflow.program'
    _description = "Academic Program"
    _inherit = ['mail.thread']
    _order = 'year_id desc, level_id, subject_id'

    subject_id = fields.Many2one('eduflow.subject', string="Subject", required=True, tracking=True)
    level_id = fields.Many2one('eduflow.level', string="Level", required=True)
    year_id = fields.Many2one('eduflow.academic.year', string="Academic Year", required=True)
    coefficient = fields.Float(string="Coefficient", default=1.0, tracking=True)
    teacher_id = fields.Many2one('eduflow.teacher', string="Teacher")
    company_id = fields.Many2one('res.company', string="Institution",
                                  default=lambda self: self.env.company)

    _sql_constraints = [
        ('subject_level_year_uniq', 'unique(subject_id, level_id, year_id)',
         "This program already exists for this subject, level and year."),
    ]
