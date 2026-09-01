# -*- coding: utf-8 -*-
from odoo import fields, models


class EduflowDashboard(models.TransientModel):
    _name = 'eduflow.dashboard'
    _description = "Management dashboard"

    year_id = fields.Many2one('eduflow.academic.year', string="Academic Year",
                               default=lambda self: self.env['eduflow.academic.year'].search(
                                   [('active_year', '=', True)], limit=1))
    total_students = fields.Integer(string="Total Students", compute='_compute_stats')
    new_students = fields.Integer(string="New Enrollments", compute='_compute_stats')
    total_teachers = fields.Integer(string="Nombre d'enseignants", compute='_compute_stats')
    total_classrooms = fields.Integer(string="Nombre de classes", compute='_compute_stats')
    absenteeism_rate = fields.Float(string="Absenteeism Rate (%)", compute='_compute_stats')
    general_average = fields.Float(string="Institution Overall Average", compute='_compute_stats')
    total_invoiced = fields.Monetary(string="Chiffre d'affaires scolaire", compute='_compute_stats',
                                      currency_field='currency_id')
    total_collected = fields.Monetary(string="Amount Collected", compute='_compute_stats',
                                       currency_field='currency_id')
    total_unpaid = fields.Monetary(string="Outstanding Amount", compute='_compute_stats',
                                    currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)

    def _compute_stats(self):
        for rec in self:
            year = rec.year_id
            enrollments = self.env['eduflow.enrollment'].search([
                ('year_id', '=', year.id), ('state', 'in', ('confirmed', 'active')),
            ]) if year else self.env['eduflow.enrollment']
            rec.total_students = len(enrollments.mapped('student_id'))
            rec.new_students = len(enrollments.filtered(lambda e: e.enrollment_type == 'new'))
            rec.total_teachers = self.env['eduflow.teacher'].search_count([('status', '=', 'active')])
            rec.total_classrooms = self.env['eduflow.classroom'].search_count(
                [('year_id', '=', year.id)]) if year else 0

            attendances = self.env['eduflow.attendance'].search([
                ('student_id', 'in', enrollments.mapped('student_id').ids),
            ])
            total_att = len(attendances)
            absent_att = len(attendances.filtered(lambda a: a.state == 'absent'))
            rec.absenteeism_rate = round((absent_att / total_att) * 100, 2) if total_att else 0.0

            report_cards = self.env['eduflow.report.card'].search([('year_id', '=', year.id)]) \
                if year else self.env['eduflow.report.card']
            rec.general_average = round(
                sum(report_cards.mapped('general_average')) / len(report_cards), 2
            ) if report_cards else 0.0

            fees = self.env['eduflow.fee'].search([('year_id', '=', year.id)]) \
                if year else self.env['eduflow.fee']
            rec.total_invoiced = sum(fees.mapped('amount'))
            rec.total_collected = sum(fees.mapped('paid_amount'))
            rec.total_unpaid = sum(fees.mapped('remaining_amount'))

    def action_view_students(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'eduflow.student',
            'view_mode': 'list,form',
            'name': 'Students',
        }

    def action_view_unpaid(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'eduflow.fee',
            'view_mode': 'list,form',
            'name': 'Overdue',
            'domain': [('state', 'in', ('overdue', 'partial', 'pending')), ('year_id', '=', self.year_id.id)],
        }
