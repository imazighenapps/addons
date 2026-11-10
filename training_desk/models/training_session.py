# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class TrainingSession(models.Model):
    _name = "training.session"
    _description = "Training Session"
    _inherit = ["mail.thread"]
    _order = "date_start desc, id desc"

    name = fields.Char(required=True, tracking=True)
    topic = fields.Char(required=True, tracking=True)
    trainer_id = fields.Many2one(
        "hr.employee", string="Trainer", required=True, tracking=True)
    date_start = fields.Date(required=True, tracking=True)
    date_end = fields.Date(required=True, tracking=True)
    capacity = fields.Integer(default=10, required=True)
    state = fields.Selection(
        [("draft", "Draft"), ("confirmed", "Confirmed"),
         ("done", "Done"), ("cancelled", "Cancelled")],
        default="draft", required=True, tracking=True, index=True)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)
    attendance_ids = fields.One2many(
        "training.attendance", "session_id", string="Attendance")
    attendee_count = fields.Integer(
        string="Attendees", compute="_compute_attendance_counts", store=True)
    certificate_count = fields.Integer(
        string="Certificates", compute="_compute_attendance_counts", store=True)
    active = fields.Boolean(default=True)
    note = fields.Text()

    @api.depends("attendance_ids", "attendance_ids.present",
                 "attendance_ids.certificate_issued")
    def _compute_attendance_counts(self):
        for session in self:
            present = session.attendance_ids.filtered(lambda a: a.present)
            session.attendee_count = len(present)
            session.certificate_count = len(
                session.attendance_ids.filtered(
                    lambda a: a.certificate_issued))

    @api.constrains("date_start", "date_end")
    def _check_dates(self):
        for session in self:
            if session.date_end < session.date_start:
                raise ValidationError(_(
                    "The end date of %s cannot be before the start date.",
                    session.name))

    @api.constrains("capacity")
    def _check_capacity(self):
        for session in self:
            if session.capacity <= 0:
                raise ValidationError(_(
                    "The capacity of %s must be greater than zero.",
                    session.name))

    @api.constrains("capacity", "attendance_ids")
    def _check_capacity_limit(self):
        for session in self:
            if session.capacity and len(session.attendance_ids) > session.capacity:
                raise ValidationError(_(
                    "The number of participants cannot exceed the capacity "
                    "of %s.", session.name))

    def action_confirm(self):
        for session in self:
            if session.state != "draft":
                raise ValidationError(_(
                    "Only draft sessions can be confirmed."))
            session.state = "confirmed"
            session.message_post(body=_("Training session confirmed."))
        return True

    def action_done(self):
        for session in self:
            if session.state != "confirmed":
                raise ValidationError(_(
                    "Only confirmed sessions can be completed."))
            session.state = "done"
            session.message_post(body=_("Training session completed."))
        return True

    def action_cancel(self):
        for session in self:
            if session.state == "done":
                raise ValidationError(_(
                    "Completed sessions cannot be cancelled."))
            if session.state == "cancelled":
                raise ValidationError(_(
                    "The session is already cancelled."))
            session.state = "cancelled"
            session.message_post(body=_("Training session cancelled."))
        return True

    def action_reset_draft(self):
        for session in self:
            if session.state == "draft":
                raise ValidationError(_(
                    "The session is already in draft."))
            session.state = "draft"
            session.message_post(body=_("Training session reset to draft."))
        return True
