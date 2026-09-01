# -*- coding: utf-8 -*-
from odoo import fields, models


class EduflowLevel(models.Model):
    _name = 'eduflow.level'
    _description = "Level scolaire"
    _order = 'sequence, name'

    name = fields.Char(string="Level", required=True, help="E.g. Primary, Middle School, High School")
    sequence = fields.Integer(string="Sequence", default=10)
    cycle = fields.Selection([
        ('primary', 'Primary'),
        ('middle', 'Middle School'),
        ('high', 'High School'),
        ('other', 'Autre'),
    ], string="Cycle", default='other')
    classroom_ids = fields.One2many('eduflow.classroom', 'level_id', string="Classs")
    subject_ids = fields.One2many('eduflow.subject', 'level_id', string="Subjects")
