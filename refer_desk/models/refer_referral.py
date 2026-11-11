# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class ReferReferral(models.Model):
    _name = "refer.referral"
    _description = "Referral"
    _inherit = ["mail.thread"]
    _order = "referred_on desc, id desc"

    name = fields.Char(
        required=True,
        default=lambda self: _("Referral %s")
        % fields.Date.context_today(self))
    code_id = fields.Many2one(
        "refer.code", string="Referral Code", required=True,
        ondelete="cascade", index=True, tracking=True)
    referred_name = fields.Char(
        string="Referred Friend", required=True, tracking=True)
    referred_on = fields.Date(
        string="Referred On", required=True, default=fields.Date.context_today,
        tracking=True)
    order_amount = fields.Monetary(
        string="Order Amount", currency_field="currency_id", default=0.0)
    reward_amount = fields.Monetary(
        string="Reward", currency_field="currency_id", default=0.0)
    credited_on = fields.Date(string="Credited On", readonly=True, copy=False)
    state = fields.Selection(
        [("pending", "Pending"), ("credited", "Credited"),
         ("cancelled", "Cancelled")],
        default="pending", required=True, tracking=True, index=True)
    currency_id = fields.Many2one(
        related="code_id.currency_id", store=True, readonly=True)
    company_id = fields.Many2one(
        related="code_id.company_id", store=True, readonly=True, index=True)
    note = fields.Text()

    @api.constrains("order_amount", "reward_amount")
    def _check_amounts(self):
        for referral in self:
            if referral.order_amount < 0:
                raise ValidationError(_(
                    "The order amount of %s cannot be negative.",
                    referral.referred_name))
            if referral.reward_amount < 0:
                raise ValidationError(_(
                    "The reward of %s cannot be negative.",
                    referral.referred_name))

    def action_credit(self):
        for referral in self:
            if referral.state != "pending":
                raise UserError(_(
                    "Only pending referrals can be credited."))
            if referral.code_id.state != "active":
                raise UserError(_(
                    "Rewards cannot be credited on a closed code."))
            referral.write({
                "state": "credited",
                "credited_on": fields.Date.context_today(referral),
            })
            referral.message_post(body=_("The referral reward was credited."))
        return True

    def action_cancel(self):
        for referral in self:
            if referral.state != "pending":
                raise UserError(_(
                    "Only pending referrals can be cancelled."))
            referral.state = "cancelled"
            referral.message_post(body=_("The referral was cancelled."))
        return True
