# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class RoundRule(models.Model):
    _name = "round.rule"
    _description = "Rounding Write-Off Rule"
    _inherit = ["mail.thread"]
    _order = "name"

    name = fields.Char(required=True, tracking=True)
    max_amount = fields.Monetary(
        string="Maximum Amount", currency_field="currency_id", required=True,
        default=0.05, tracking=True,
        help="Largest difference this rule is allowed to absorb.")
    reason = fields.Char(
        required=True,
        help="Reason booked when a difference is cleared with this rule.")
    currency_id = fields.Many2one(
        "res.currency", required=True,
        default=lambda self: self.env.company.currency_id)
    writeoff_ids = fields.One2many(
        "round.writeoff", "rule_id", string="Write-Offs")
    writeoff_count = fields.Integer(
        string="Write-Offs", compute="_compute_writeoff_stats", store=True)
    cleared_amount = fields.Monetary(
        string="Cleared Amount", currency_field="currency_id",
        compute="_compute_writeoff_stats", store=True,
        help="Total amount absorbed by posted write-offs on this rule.")
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)
    note = fields.Text()

    @api.depends("writeoff_ids", "writeoff_ids.state", "writeoff_ids.amount")
    def _compute_writeoff_stats(self):
        for rule in self:
            lines = rule.writeoff_ids
            rule.writeoff_count = len(lines)
            rule.cleared_amount = sum(lines.filtered(
                lambda line: line.state == "posted").mapped("amount"))

    @api.constrains("max_amount")
    def _check_max_amount(self):
        for rule in self:
            if rule.max_amount <= 0.0:
                raise ValidationError(_(
                    "The maximum amount of rule %s must be above zero.",
                    rule.name))
