# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class DutyRoster(models.Model):
    _name = "duty.roster"
    _description = "Duty Roster"
    _inherit = ["mail.thread"]
    _order = "date_start desc, id desc"

    name = fields.Char(required=True, tracking=True)
    date_start = fields.Date(required=True, tracking=True)
    date_end = fields.Date(required=True, tracking=True)
    state = fields.Selection(
        [("draft", "Draft"), ("published", "Published"),
         ("closed", "Closed")],
        default="draft", required=True, tracking=True, index=True)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)
    slot_ids = fields.One2many("duty.slot", "roster_id", string="Slots")
    slot_count = fields.Integer(
        string="Slots", compute="_compute_totals", store=True)
    compensation_total = fields.Float(
        string="Compensation Total", compute="_compute_totals", store=True)
    note = fields.Text()
    active = fields.Boolean(default=True)

    @api.depends("slot_ids", "slot_ids.compensation")
    def _compute_totals(self):
        for roster in self:
            roster.slot_count = len(roster.slot_ids)
            roster.compensation_total = sum(roster.slot_ids.mapped("compensation"))

    @api.constrains("date_start", "date_end")
    def _check_dates(self):
        for roster in self:
            if roster.date_end < roster.date_start:
                raise ValidationError(_(
                    "The end date of %s cannot be before the start date.",
                    roster.name))

    def action_publish(self):
        for roster in self:
            if roster.state != "draft":
                raise ValidationError(_(
                    "Only draft rosters can be published."))
            if not roster.slot_ids:
                raise ValidationError(_(
                    "Add at least one duty slot before publishing %s.",
                    roster.name))
            roster.state = "published"
            roster.message_post(body=_("Roster published."))
        return True

    def action_close(self):
        for roster in self:
            if roster.state != "published":
                raise ValidationError(_(
                    "Only published rosters can be closed."))
            roster.state = "closed"
            roster.message_post(body=_("Roster closed."))
        return True

    def action_reset_draft(self):
        for roster in self:
            if roster.state == "draft":
                raise ValidationError(_(
                    "The roster is already in draft."))
            roster.state = "draft"
            roster.message_post(body=_("Roster reset to draft."))
        return True
