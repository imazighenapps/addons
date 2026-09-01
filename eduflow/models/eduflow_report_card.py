# -*- coding: utf-8 -*-
from odoo import api, fields, models


class EduflowReportCard(models.Model):
    _name = 'eduflow.report.card'
    _description = "Report Card"
    _inherit = ['mail.thread']
    _order = 'period_id desc, student_id'

    student_id = fields.Many2one('eduflow.student', string="Student", required=True)
    classroom_id = fields.Many2one('eduflow.classroom', string="Class", required=True)
    year_id = fields.Many2one('eduflow.academic.year', string="Academic Year", required=True)
    period_id = fields.Many2one('eduflow.academic.period', string="Period", required=True)
    line_ids = fields.One2many('eduflow.report.card.line', 'report_card_id',
                                string="Averages by Subject")
    general_average = fields.Float(string="Overall Average", compute='_compute_general_average',
                                    store=True, digits=(5, 2), tracking=True)
    ranking = fields.Integer(string="Ranking", compute='_compute_ranking',
                              help="Recalculated on each display (not stored) because it depends on "
                                   "the ranking of other students in the class, which may change "
                                   "independently of this report card.")
    absence_count = fields.Integer(string="Absences", compute='_compute_absences',
                                    help="Recalculated on each display (not stored) because it depends "
                                         "on entered attendance, which may be added after "
                                         "the generation of the report card.")
    council_decision = fields.Selection([
        ('pass', 'Pass'),
        ('repeat', 'Repeat'),
        ('orientation', 'Orientation'),
        ('exclusion', 'Exclusion'),
        ('custom', 'Custom Decision'),
    ], string="Board Decision", tracking=True)
    council_notes = fields.Text(string="Board Notes")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('generated', 'Generated'),
        ('published', 'Published (Parent Portal)'),
    ], string="Status", default='draft', tracking=True)
    company_id = fields.Many2one('res.company', string="Institution",
                                  related='classroom_id.company_id', store=True, readonly=True)

    _sql_constraints = [
        ('student_period_uniq', 'unique(student_id, period_id)',
         "A report card already exists for this student for this period."),
    ]

    @api.depends('line_ids.average', 'line_ids.coefficient')
    def _compute_general_average(self):
        for rec in self:
            total_weighted = sum(l.average * l.coefficient for l in rec.line_ids)
            total_coeff = sum(l.coefficient for l in rec.line_ids)
            rec.general_average = round(total_weighted / total_coeff, 2) if total_coeff else 0.0

    @api.depends('general_average', 'classroom_id')
    def _compute_ranking(self):
        for rec in self:
            if not rec.classroom_id or not rec.period_id:
                rec.ranking = 0
                continue
            classmates = self.search([
                ('classroom_id', '=', rec.classroom_id.id),
                ('period_id', '=', rec.period_id.id),
            ], order='general_average desc')
            rec.ranking = (list(classmates.ids).index(rec.id) + 1) if rec.id in classmates.ids else 0

    @api.depends('student_id', 'period_id')
    def _compute_absences(self):
        for rec in self:
            if rec.period_id and rec.period_id.date_start and rec.period_id.date_end:
                rec.absence_count = self.env['eduflow.attendance'].search_count([
                    ('student_id', '=', rec.student_id.id),
                    ('state', '=', 'absent'),
                    ('date', '>=', rec.period_id.date_start),
                    ('date', '<=', rec.period_id.date_end),
                ])
            else:
                rec.absence_count = 0

    def action_generate_lines(self):
        """Rebuild average lines by subject from existing grades."""
        for rec in self:
            rec.line_ids.unlink()
            grades = self.env['eduflow.grade'].search([
                ('student_id', '=', rec.student_id.id),
                ('exam_id.period_id', '=', rec.period_id.id),
                ('exam_id.classroom_id', '=', rec.classroom_id.id),
            ])
            subjects = grades.mapped('subject_id')
            lines = []
            for subject in subjects:
                subject_grades = grades.filtered(lambda g: g.subject_id == subject)
                weighted = sum(g.grade * g.exam_id.coefficient for g in subject_grades)
                total_coeff = sum(g.exam_id.coefficient for g in subject_grades)
                avg = round(weighted / total_coeff, 2) if total_coeff else 0.0
                lines.append((0, 0, {
                    'subject_id': subject.id,
                    'average': avg,
                    'coefficient': subject.coefficient,
                }))
            rec.line_ids = lines
            rec.state = 'generated'

    def action_publish(self):
        self.write({'state': 'published'})

    def action_print_report_card(self):
        return self.env.ref('eduflow.action_report_eduflow_report_card').report_action(self)


class EduflowReportCardLine(models.Model):
    _name = 'eduflow.report.card.line'
    _description = "Report Card Line (average by subject)"

    report_card_id = fields.Many2one('eduflow.report.card', required=True, ondelete='cascade')
    subject_id = fields.Many2one('eduflow.subject', string="Subject", required=True)
    average = fields.Float(string="Average (/20)", digits=(5, 2))
    coefficient = fields.Float(string="Coefficient", default=1.0)
    appreciation = fields.Char(string="Comment")
