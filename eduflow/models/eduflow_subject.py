# -*- coding: utf-8 -*-
from odoo import fields, models


class EduflowSubject(models.Model):
    _name = 'eduflow.subject'
    _description = "Subject"
    _inherit = ['mail.thread']
    _order = 'level_id, name'

    code = fields.Char(string="Code", required=True, tracking=True)
    name = fields.Char(string="Nom", required=True, tracking=True)
    description = fields.Text(string="Description")
    coefficient = fields.Float(string="Coefficient", default=1.0, tracking=True)
    hours = fields.Float(string="Volume horaire (h/semaine)")
    level_id = fields.Many2one('eduflow.level', string="Related Level", required=True)
    teacher_id = fields.Many2one('eduflow.teacher', string="Teacher responsable")
    # F4.1 -- eduflow.subject was the only setup model without company_id,
    # inconsistent with eduflow.level/eduflow.classroom/eduflow.fee.type.
    company_id = fields.Many2one('res.company', string="Institution",
                                  default=lambda self: self.env.company)

    _sql_constraints = [
        ('code_level_uniq', 'unique(code, level_id)',
         "This subject code already exists for this level."),
    ]
