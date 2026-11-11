# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class RecoverClaim(models.Model):
    _name = "recover.claim"
    _description = "Recoverable Claim"
    _inherit = ["mail.thread"]
    _order = "due_on asc, id desc"

    name = fields.Char(required=True, tracking=True)
    partner_name = fields.Char(
        string="Counterparty", required=True, tracking=True,
        help="Customer or supplier who owes the amount back.")
    origin_ref = fields.Char(
        string="Origin Reference",
        help="Invoice, contract or email reference for the claim.")
    claim_kind = fields.Selection(
        [("refund", "Refund"), ("rebate", "Rebate"),
         ("reimbursement", "Reimbursement"), ("other", "Other")],
        default="refund", required=True, tracking=True)
    amount_expected = fields.Monetary(
        string="Amount Expected", currency_field="currency_id", required=True,
        tracking=True, help="Amount the company expects to recover.")
    amount_recovered = fields.Monetary(
        string="Amount Recovered", currency_field="currency_id", default=0.0,
        copy=False, tracking=True,
        help="Amount actually recovered on this claim.")
    currency_id = fields.Many2one(
        "res.currency", required=True,
        default=lambda self: self.env.company.currency_id)
    due_on = fields.Date(
        string="Expected On", required=True, tracking=True,
        help="Date by which the amount should be recovered.")
    state = fields.Selection(
        [("open", "Open"), ("recovered", "Recovered"),
         ("written_off", "Written Off")],
        default="open", required=True, copy=False, tracking=True, index=True)
    recovered_on = fields.Date(string="Recovered On", readonly=True,
                               copy=False)
    action_ids = fields.One2many(
        "recover.action", "claim_id", string="Chase Actions")
    action_count = fields.Integer(
        string="Chase Actions", compute="_compute_action_count", store=True)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)
    note = fields.Text()

    @api.depends("action_ids")
    def _compute_action_count(self):
        for claim in self:
            claim.action_count = len(claim.action_ids)

    @api.constrains("amount_expected", "amount_recovered")
    def _check_amounts(self):
        for claim in self:
            if claim.amount_expected <= 0.0:
                raise ValidationError(_(
                    "The expected amount of %s must be above zero.",
                    claim.name))
            if claim.amount_recovered < 0.0:
                raise ValidationError(_(
                    "The recovered amount of %s cannot be negative.",
                    claim.name))
            if claim.amount_recovered > claim.amount_expected:
                raise ValidationError(_(
                    "The recovered amount of %s cannot exceed the expected "
                    "amount.", claim.name))

    def action_recover(self):
        for claim in self:
            if claim.state != "open":
                raise ValidationError(_(
                    "Only an open claim can be recovered."))
            claim.write({
                "state": "recovered",
                "amount_recovered": claim.amount_expected,
                "recovered_on": fields.Date.context_today(claim),
            })
            claim.message_post(body=_(
                "The claim was marked as fully recovered."))
        return True

    def action_write_off(self):
        for claim in self:
            if claim.state != "open":
                raise ValidationError(_(
                    "Only an open claim can be written off."))
            claim.state = "written_off"
            claim.message_post(body=_(
                "The claim was written off as unrecoverable."))
        return True
