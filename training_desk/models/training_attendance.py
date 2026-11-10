# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class TrainingAttendance(models.Model):
    _name = "training.attendance"
    _description = "Training Attendance"
    _inherit = ["mail.thread"]
    _order = "id desc"

    name = fields.Char(
        compute="_compute_name", store=True)
    session_id = fields.Many2one(
        "training.session", string="Session", required=True,
        ondelete="cascade", index=True, tracking=True)
    employee_id = fields.Many2one(
        "hr.employee", string="Participant", required=True, tracking=True,
        index=True)
    present = fields.Boolean(default=False, tracking=True)
    certificate_issued = fields.Boolean(
        string="Certificate Issued", default=False, tracking=True)
    certificate_date = fields.Date(string="Certificate Date")
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)
    note = fields.Text()

    @api.depends("session_id.name", "employee_id.name")
    def _compute_name(self):
        for line in self:
            session = line.session_id.name or _("Session")
            employee = line.employee_id.name or _("Participant")
            line.name = "%s - %s" % (session, employee)

    @api.constrains("session_id", "employee_id")
    def _check_unique_participant(self):
        for line in self:
            duplicates = self.search([
                ("id", "!=", line.id),
                ("session_id", "=", line.session_id.id),
                ("employee_id", "=", line.employee_id.id),
            ], limit=1)
            if duplicates:
                raise ValidationError(_(
                    "Participant %s is already registered in session %s.",
                    line.employee_id.name, line.session_id.name))

    @api.constrains("session_id")
    def _check_session_capacity(self):
        for line in self:
            session = line.session_id
            if session and session.capacity and len(session.attendance_ids) > session.capacity:
                raise ValidationError(_(
                    "The number of participants cannot exceed the capacity "
                    "of %s.", session.name))

    @api.constrains("certificate_issued", "present")
    def _check_certificate_requires_presence(self):
        for line in self:
            if line.certificate_issued and not line.present:
                raise ValidationError(_(
                    "A certificate can only be issued to a present "
                    "participant in %s.", line.session_id.name))

    def action_mark_present(self):
        for line in self:
            line.present = True
            line.message_post(body=_("Participant marked as present."))
        return True

    def action_issue_certificate(self):
        for line in self:
            if not line.present:
                raise ValidationError(_(
                    "Mark the participant as present before issuing a "
                    "certificate."))
            if line.certificate_issued:
                raise ValidationError(_(
                    "The certificate is already issued for %s.",
                    line.employee_id.name))
            line.write({
                "certificate_issued": True,
                "certificate_date": fields.Date.context_today(line),
            })
            line.message_post(body=_("Certificate issued."))
        return True
