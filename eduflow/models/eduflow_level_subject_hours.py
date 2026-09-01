# -*- coding: utf-8 -*-
from odoo import api, fields, models

class EduflowLevelSubjectHours(models.Model):
    _name = 'eduflow.level.subject.hours'
    _description = "Hours per Level/Subject"
    _order = 'level_id, subject_id'

    level_id = fields.Many2one('eduflow.level', string="Level", required=True)
    subject_id = fields.Many2one('eduflow.subject', string="Subject", required=True)
    year_id = fields.Many2one('eduflow.academic.year', string="Academic Year")
    hours_per_week = fields.Float(string="Hours / Week", required=True, default=3.0)
    room_type = fields.Selection([
        ('classroom', 'Classroom'),
        ('lab', 'Laboratory'),
        ('gym', 'Gym'),
        ('any', 'Any'),
    ], string="Required Room Type", default='classroom')
    morning_only = fields.Boolean(string="Morning Only", default=False)
    consecutive = fields.Boolean(string="Avoid Consecutive", default=True, help="Avoid same subject twice in a row")
    sessions_per_week = fields.Integer(string="Sessions / Week", compute="_compute_sessions", store=True, readonly=True)

    @api.depends("hours_per_week")
    def _compute_sessions(self):
        for rec in self:
            rec.sessions_per_week = int(rec.hours_per_week)
    company_id = fields.Many2one('res.company', string="Institution", default=lambda self: self.env.company)

    _sql_constraints = [
        ('level_subject_year_uniq', 'unique(level_id, subject_id, year_id)',
         "Hours already defined for this level+subject+year."),
    ]
