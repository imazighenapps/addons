# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AppointmentLog(models.Model):
    _name = "appointment.log"
    _description = "Appointment Log"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date desc, id desc"

    name = fields.Char(string="Subject", required=True, tracking=True)
    partner_id = fields.Many2one(
        "res.partner", string="Contact", required=True, index=True, tracking=True)
    user_id = fields.Many2one(
        "res.users", string="Responsible", default=lambda self: self.env.user,
        required=True, tracking=True)
    date = fields.Datetime(
        string="Date & Time", required=True, default=fields.Datetime.now, tracking=True)
    location = fields.Char(string="Location")
    outcome = fields.Text(string="Outcome")
    next_action = fields.Text(string="Next Action")
    followup_date = fields.Date(string="Follow-up Date")
    state = fields.Selection(
        [("planned", "Planned"), ("done", "Done"), ("cancelled", "Cancelled")],
        default="planned", required=True, tracking=True, index=True)
    note = fields.Text()
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True,
        index=True)

    def action_done(self):
        for rec in self:
            if rec.state != "planned":
                raise UserError(_("Only a planned appointment can be marked done."))
            rec.state = "done"

    def action_cancel(self):
        for rec in self:
            if rec.state == "done":
                raise UserError(_("A completed appointment cannot be cancelled."))
            rec.state = "cancelled"

    def action_reset(self):
        for rec in self:
            rec.state = "planned"
