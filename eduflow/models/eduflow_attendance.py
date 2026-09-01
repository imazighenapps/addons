# -*- coding: utf-8 -*-
from odoo import fields, models


class EduflowAttendance(models.Model):
    _name = 'eduflow.attendance'
    _description = "Attendance"
    _inherit = ['mail.thread']
    _order = 'date desc'

    student_id = fields.Many2one('eduflow.student', string="Student", required=True)
    classroom_id = fields.Many2one('eduflow.classroom', string="Class", required=True)
    session_id = fields.Many2one('eduflow.timetable.session', string="Session")
    date = fields.Date(string="Date", required=True, default=fields.Date.context_today)
    state = fields.Selection([
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('justified', 'Justified Absence'),
    ], string="Status", default='present', required=True)
    reason = fields.Char(string="Reason")
    comment = fields.Text(string="Comment")
    justification_document = fields.Binary(string="Supporting Document")
    notified_parent = fields.Boolean(string="Parent Notified", default=False)
    company_id = fields.Many2one('res.company', string="Institution",
                                  related='classroom_id.company_id', store=True, readonly=True)

    def action_notify_parent(self):
        """Sends a simple notification to guardians allowed to communicate."""
        for rec in self:
            parents = rec.student_id.parent_rel_ids.filtered('can_communicate').mapped('parent_id')
            if parents:
                body = (f"Your child {rec.student_id.display_name} has been marked "
                        f"'{dict(rec._fields['state'].selection).get(rec.state)}' le {rec.date}.")
                for parent in parents:
                    if parent.partner_id:
                        rec.message_notify(
                            partner_ids=[parent.partner_id.id],
                            body=body,
                            subject="Attendance Notification",
                        )
            rec.notified_parent = True
