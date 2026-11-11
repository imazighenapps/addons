# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class FeeLine(models.Model):
    _name = "fee.line"
    _description = "Billed Payment Fee"
    _inherit = ["mail.thread"]
    _order = "billed_on desc, id desc"

    name = fields.Char(
        required=True,
        default=lambda self: _("Fee %s") % fields.Date.context_today(self),
        help="Reference of the billed fee, generated at creation.")
    contract_id = fields.Many2one(
        "fee.contract", string="Contract", required=True,
        ondelete="cascade", index=True, tracking=True)
    billed_on = fields.Date(
        string="Billed On", required=True,
        default=fields.Date.context_today, tracking=True)
    settled_amount = fields.Monetary(
        string="Settled Amount", currency_field="currency_id", required=True,
        help="Amount settled by the platform for the transaction.")
    charged_fee = fields.Monetary(
        string="Charged Fee", currency_field="currency_id", required=True,
        help="Fee actually charged by the payment platform.")
    expected_fee = fields.Monetary(
        string="Expected Fee", currency_field="currency_id",
        compute="_compute_variance", store=True,
        help="Fee expected from the signed contract.")
    variance_amount = fields.Monetary(
        string="Variance", currency_field="currency_id",
        compute="_compute_variance", store=True,
        help="Difference between the charged fee and the expected fee.")
    currency_id = fields.Many2one(
        "res.currency", related="contract_id.currency_id", store=True,
        readonly=True)
    state = fields.Selection(
        [("draft", "Draft"), ("disputed", "Disputed"),
         ("recovered", "Recovered"), ("waived", "Waived")],
        default="draft", required=True, copy=False, tracking=True, index=True)
    recovered_amount = fields.Monetary(
        string="Recovered Amount", currency_field="currency_id", default=0.0,
        copy=False,
        help="Amount recovered from the platform after a dispute.")
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)
    note = fields.Text()

    @api.depends("contract_id", "contract_id.rate_percent",
                 "contract_id.fixed_fee", "settled_amount", "charged_fee")
    def _compute_variance(self):
        for line in self:
            expected = 0.0
            if line.contract_id:
                expected = (
                    line.settled_amount * line.contract_id.rate_percent / 100.0
                    + line.contract_id.fixed_fee
                )
            line.expected_fee = expected
            line.variance_amount = line.charged_fee - expected

    @api.constrains("settled_amount", "charged_fee", "recovered_amount")
    def _check_amounts(self):
        for line in self:
            if line.settled_amount < 0.0:
                raise ValidationError(_(
                    "The settled amount of %s cannot be negative.",
                    line.name))
            if line.charged_fee < 0.0:
                raise ValidationError(_(
                    "The charged fee of %s cannot be negative.",
                    line.name))
            if line.recovered_amount < 0.0:
                raise ValidationError(_(
                    "The recovered amount of %s cannot be negative.",
                    line.name))

    def action_dispute(self):
        for line in self:
            if line.state != "draft":
                raise ValidationError(_(
                    "Only a draft fee line can be disputed."))
            if abs(line.variance_amount) <= 0.00001:
                raise ValidationError(_(
                    "Fee line %s has no variance to dispute.", line.name))
            line.state = "disputed"
            line.message_post(body=_("The fee variance was opened as a dispute."))
        return True

    def action_recover(self):
        for line in self:
            if line.state != "disputed":
                raise ValidationError(_(
                    "Only a disputed fee line can be recovered."))
            line.write({
                "state": "recovered",
                "recovered_amount": line.variance_amount,
            })
            line.message_post(body=_(
                "The unexpected fee was marked as recovered."))
        return True

    def action_waive(self):
        for line in self:
            if line.state != "disputed":
                raise ValidationError(_(
                    "Only a disputed fee line can be waived."))
            line.state = "waived"
            line.message_post(body=_(
                "The fee variance was waived."))
        return True
