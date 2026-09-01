# -*- coding: utf-8 -*-
from odoo import _, api, fields, models


class EduflowAttendanceWizard(models.TransientModel):
    """F2.1 -- 'Take Attendance' assistant: pick a class and a date, get all
    active students pre-filled as 'Present', correct exceptions, validate
    once for the whole class instead of one eduflow.attendance at a time."""
    _name = 'eduflow.attendance.wizard'
    _description = "Take Attendance"

    classroom_id = fields.Many2one('eduflow.classroom', string="Class", required=True)
    session_id = fields.Many2one(
        'eduflow.timetable.session', string="Session",
        domain="[('classroom_id', '=', classroom_id)]")
    date = fields.Date(string="Date", required=True, default=fields.Date.context_today)
    line_ids = fields.One2many('eduflow.attendance.wizard.line', 'wizard_id', string="Students")
    notify_absentees = fields.Boolean(string="Notify guardians of absentees", default=True)

    @api.onchange('classroom_id', 'date')
    def _onchange_classroom_date(self):
        if not (self.classroom_id and self.date):
            self.line_ids = [(5, 0, 0)]
            return
        enrollments = self.env['eduflow.enrollment'].search([
            ('classroom_id', '=', self.classroom_id.id),
            ('state', 'in', ('confirmed', 'active')),
        ])
        existing = self.env['eduflow.attendance'].search([
            ('classroom_id', '=', self.classroom_id.id),
            ('date', '=', self.date),
        ])
        existing_by_student = {att.student_id.id: att for att in existing}
        lines = []
        for enrollment in enrollments:
            student = enrollment.student_id
            prev = existing_by_student.get(student.id)
            lines.append((0, 0, {
                'student_id': student.id,
                'state': prev.state if prev else 'present',
                'reason': prev.reason if prev else False,
                'attendance_id': prev.id if prev else False,
            }))
        self.line_ids = [(5, 0, 0)] + lines

    def action_validate(self):
        self.ensure_one()
        Attendance = self.env['eduflow.attendance']
        created = Attendance
        for line in self.line_ids:
            vals = {
                'student_id': line.student_id.id,
                'classroom_id': self.classroom_id.id,
                'session_id': self.session_id.id,
                'date': self.date,
                'state': line.state,
                'reason': line.reason,
            }
            if line.attendance_id:
                line.attendance_id.write(vals)
                created |= line.attendance_id
            else:
                created |= Attendance.create(vals)
        if self.notify_absentees:
            created.filtered(lambda a: a.state == 'absent' and not a.notified_parent)\
                .action_notify_parent()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'eduflow.attendance',
            'view_mode': 'list,form',
            'domain': [('id', 'in', created.ids)],
            'name': _("Attendance - %s") % self.classroom_id.display_name,
        }


class EduflowAttendanceWizardLine(models.TransientModel):
    _name = 'eduflow.attendance.wizard.line'
    _description = "Take Attendance - Student Line"

    wizard_id = fields.Many2one('eduflow.attendance.wizard', required=True, ondelete='cascade')
    student_id = fields.Many2one('eduflow.student', string="Student", required=True)
    attendance_id = fields.Many2one('eduflow.attendance', string="Existing Record")
    state = fields.Selection([
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('justified', 'Justified Absence'),
    ], string="Status", default='present', required=True)
    reason = fields.Char(string="Reason")
