# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ToolboxTalk(models.Model):
    _name = "toolbox.talk"
    _description = "Toolbox Talk"
    _inherit = ["mail.thread"]
    _order = "talk_on desc, id desc"

    name = fields.Char(
        string="Topic", required=True, tracking=True,
        help="Topic covered during the safety briefing.")
    talk_on = fields.Date(
        string="Date", required=True, default=fields.Date.context_today,
        tracking=True)
    location = fields.Char(
        help="Place where the toolbox talk was held.")
    leader_id = fields.Many2one(
        "hr.employee", string="Leader", required=True, tracking=True,
        help="Employee who led the briefing.")
    attendance_ids = fields.One2many(
        "toolbox.attendance", "talk_id", string="Attendance")
    attendance_count = fields.Integer(
        string="Attendees", compute="_compute_attendance")
    signed_count = fields.Integer(
        string="Signed", compute="_compute_attendance")
    state = fields.Selection(
        [("planned", "Planned"), ("done", "Completed")],
        default="planned", required=True, copy=False, tracking=True,
        index=True)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)
    note = fields.Text()

    @api.depends("attendance_ids", "attendance_ids.signed")
    def _compute_attendance(self):
        for talk in self:
            talk.attendance_count = len(talk.attendance_ids)
            talk.signed_count = len(talk.attendance_ids.filtered("signed"))

    def action_complete(self):
        for talk in self:
            if talk.state != "planned":
                raise ValidationError(_(
                    "The toolbox talk %s is already completed.", talk.name))
            talk.write({"state": "done"})
            talk.message_post(body=_(
                "The toolbox talk was completed and recorded."))
        return True
