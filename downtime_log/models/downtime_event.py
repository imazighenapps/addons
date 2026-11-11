# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class DowntimeEvent(models.Model):
    _name = "downtime.event"
    _description = "Downtime Event"
    _inherit = ["mail.thread"]
    _order = "start_at desc, id desc"

    name = fields.Char(
        required=True, tracking=True,
        default=lambda self: _("Stop %s") % fields.Date.context_today(self),
        help="Reference of the downtime event.")
    machine_id = fields.Many2one(
        "downtime.machine", string="Machine", required=True,
        ondelete="cascade", index=True, tracking=True)
    reason = fields.Char(
        required=True, tracking=True,
        help="Short reason describing why the machine stopped.")
    start_at = fields.Datetime(
        string="Start", required=True, default=fields.Datetime.now,
        tracking=True)
    end_at = fields.Datetime(string="End", tracking=True)
    duration_minutes = fields.Float(
        string="Duration (min)", compute="_compute_duration", store=True,
        help="Duration of the stop in minutes.")
    state = fields.Selection(
        [("open", "Running"), ("closed", "Closed")],
        default="open", required=True, tracking=True, index=True)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)
    note = fields.Text()

    @api.depends("start_at", "end_at")
    def _compute_duration(self):
        for event in self:
            if event.start_at and event.end_at:
                delta = event.end_at - event.start_at
                event.duration_minutes = delta.total_seconds() / 60.0
            else:
                event.duration_minutes = 0.0

    @api.constrains("start_at", "end_at")
    def _check_dates(self):
        for event in self:
            if event.end_at and event.start_at and event.end_at < event.start_at:
                raise ValidationError(_(
                    "The end time of %s cannot be before its start time.",
                    event.name))

    @api.constrains("state", "end_at")
    def _check_closed_end(self):
        for event in self:
            if event.state == "closed" and not event.end_at:
                raise ValidationError(_(
                    "Set an end time before closing %s.", event.name))

    def action_close_stop(self):
        for event in self:
            if event.state == "closed":
                raise ValidationError(_(
                    "The stop event %s is already closed.", event.name))
            end_at = event.end_at or fields.Datetime.now()
            if end_at < event.start_at:
                raise ValidationError(_(
                    "The end time of %s cannot be before its start time.",
                    event.name))
            event.write({
                "state": "closed",
                "end_at": end_at,
            })
            event.message_post(body=_("The stop event has been closed."))
        return True
