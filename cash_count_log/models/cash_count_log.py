# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class CashCountLog(models.Model):
    _name = "cash.count.log"
    _description = "Cash Count"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "count_date desc, id desc"

    name = fields.Char(
        string="Reference", required=True, tracking=True, index=True,
        default=lambda self: _("New"))
    count_date = fields.Date(
        required=True, default=fields.Date.context_today, tracking=True)
    location = fields.Char(string="Location / Register", tracking=True)
    counter_id = fields.Many2one(
        "res.users", string="Counted By", default=lambda self: self.env.user,
        tracking=True)
    reviewer_id = fields.Many2one("res.users", string="Reviewed By", tracking=True)
    currency_id = fields.Many2one(
        "res.currency", default=lambda self: self.env.company.currency_id)
    expected_amount = fields.Monetary(
        string="Expected Amount", currency_field="currency_id", tracking=True)
    counted_amount = fields.Monetary(
        string="Counted Amount", currency_field="currency_id", tracking=True)
    difference = fields.Monetary(
        currency_field="currency_id", compute="_compute_difference", store=True)
    note = fields.Text(string="Notes")
    state = fields.Selection(
        [("draft", "Draft"), ("submitted", "Submitted"), ("validated", "Validated")],
        default="draft", required=True, tracking=True, index=True)
    count = fields.Integer(default=1)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                seq = self.env["ir.sequence"].next_by_code("cash.count.log")
                vals["name"] = seq or _("New")
        return super().create(vals_list)

    @api.depends("expected_amount", "counted_amount")
    def _compute_difference(self):
        for record in self:
            record.difference = (record.counted_amount or 0.0) - (record.expected_amount or 0.0)

    def action_submit(self):
        for record in self:
            if record.state != "draft":
                raise UserError(_("Only a draft count can be submitted."))
            record.state = "submitted"
        return True

    def action_validate(self):
        for record in self:
            if record.state != "submitted":
                raise UserError(_("Only a submitted count can be validated."))
            record.write({"state": "validated", "reviewer_id": self.env.user.id})
        return True

    def action_reset_draft(self):
        for record in self:
            if record.state != "submitted":
                raise UserError(_("Only a submitted count can be reset to draft."))
            record.state = "draft"
        return True
