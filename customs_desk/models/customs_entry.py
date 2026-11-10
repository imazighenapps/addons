# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class CustomsEntry(models.Model):
    _name = "customs.entry"
    _description = "Customs Entry"
    _inherit = ["mail.thread"]
    _order = "declaration_date desc, id desc"

    name = fields.Char(
        string="Entry Reference", required=True, copy=False, tracking=True,
        help="Declaration or entry number provided by the broker.")
    partner_id = fields.Many2one(
        "res.partner", string="Supplier", required=True, tracking=True)
    country_id = fields.Many2one(
        "res.country", string="Origin Country", required=True, tracking=True)
    declaration_date = fields.Date(
        required=True, default=fields.Date.context_today, tracking=True)
    state = fields.Selection(
        [("draft", "Draft"), ("checked", "Checked"), ("cleared", "Cleared")],
        default="draft", required=True, copy=False, tracking=True, index=True)
    cleared_on = fields.Date(readonly=True, copy=False)
    line_ids = fields.One2many(
        "customs.entry.line", "entry_id", string="Entry Lines", copy=True)
    line_count = fields.Integer(
        string="Lines", compute="_compute_totals", store=True)
    total_value = fields.Monetary(
        string="Total Customs Value", compute="_compute_totals", store=True,
        currency_field="currency_id")
    total_duty = fields.Monetary(
        string="Total Duty", compute="_compute_totals", store=True,
        currency_field="currency_id")
    currency_id = fields.Many2one(
        "res.currency", required=True,
        default=lambda self: self.env.company.currency_id)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)
    note = fields.Text()

    @api.depends("line_ids", "line_ids.customs_value", "line_ids.duty_amount")
    def _compute_totals(self):
        for entry in self:
            lines = entry.line_ids
            entry.line_count = len(lines)
            entry.total_value = sum(lines.mapped("customs_value"))
            entry.total_duty = sum(lines.mapped("duty_amount"))

    def _ensure_open(self):
        for entry in self:
            if entry.state == "cleared":
                raise UserError(_(
                    "The cleared entry %s cannot be changed.", entry.name))

    def write(self, vals):
        self._ensure_open()
        return super().write(vals)

    def action_check(self):
        for entry in self:
            if entry.state != "draft":
                raise UserError(_("Only a draft entry can be checked."))
            if not entry.line_ids:
                raise UserError(_(
                    "Add at least one line before checking %s.", entry.name))
            entry.state = "checked"
            entry.message_post(body=_("Entry checked."))
        return True

    def action_clear(self):
        for entry in self:
            if entry.state != "checked":
                raise UserError(_("Only a checked entry can be cleared."))
            entry.write({
                "state": "cleared",
                "cleared_on": fields.Date.context_today(entry),
            })
            entry.message_post(body=_(
                "Entry cleared with a total duty of %s.", entry.total_duty))
        return True

    def action_reset(self):
        for entry in self:
            if entry.state != "checked":
                raise UserError(_("Only a checked entry can be reset to draft."))
            entry.state = "draft"
            entry.message_post(body=_("Entry reset to draft."))
        return True
