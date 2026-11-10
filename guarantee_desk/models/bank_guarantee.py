# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class BankGuarantee(models.Model):
    _name = "bank.guarantee"
    _description = "Bank Guarantee"
    _inherit = ["mail.thread"]
    _order = "expiry_date, id desc"

    name = fields.Char(
        string="Reference", required=True, copy=False, tracking=True,
        help="Guarantee or standby letter reference given by the bank.")
    guarantee_type = fields.Selection(
        [("bid", "Bid Bond"), ("performance", "Performance Guarantee"),
         ("advance", "Advance Payment"), ("warranty", "Warranty"),
         ("standby", "Standby Letter of Credit")],
        required=True, default="performance", tracking=True)
    beneficiary_id = fields.Many2one(
        "res.partner", string="Beneficiary", required=True, tracking=True)
    issuing_bank_id = fields.Many2one(
        "res.partner", string="Issuing Bank", tracking=True)
    currency_id = fields.Many2one(
        "res.currency", required=True,
        default=lambda self: self.env.company.currency_id)
    amount = fields.Monetary(required=True, currency_field="currency_id",
                             tracking=True)
    issue_date = fields.Date(required=True, default=fields.Date.context_today,
                             tracking=True)
    expiry_date = fields.Date(required=True, tracking=True)
    state = fields.Selection(
        [("draft", "Draft"), ("active", "Active"), ("released", "Released"),
         ("cancelled", "Cancelled")],
        default="draft", required=True, copy=False, tracking=True, index=True)
    release_date = fields.Date(readonly=True, copy=False)
    release_note = fields.Text()
    renewal_ids = fields.One2many(
        "bank.guarantee.renewal", "guarantee_id", string="Renewals")
    renewal_count = fields.Integer(
        string="Renewals", compute="_compute_renewal_count", store=True)
    is_active = fields.Boolean(
        string="Active Guarantee", compute="_compute_is_active", store=True,
        help="True while the guarantee is active and not yet released.")
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)
    note = fields.Text()

    @api.depends("renewal_ids")
    def _compute_renewal_count(self):
        for guarantee in self:
            guarantee.renewal_count = len(guarantee.renewal_ids)

    @api.depends("state")
    def _compute_is_active(self):
        for guarantee in self:
            guarantee.is_active = guarantee.state == "active"

    @api.constrains("issue_date", "expiry_date")
    def _check_dates(self):
        for guarantee in self:
            if guarantee.expiry_date < guarantee.issue_date:
                raise ValidationError(_(
                    "The expiry date of %s cannot be before its issue date.",
                    guarantee.name))

    @api.constrains("release_date", "issue_date")
    def _check_release_date(self):
        for guarantee in self:
            if guarantee.release_date and guarantee.release_date < guarantee.issue_date:
                raise ValidationError(_(
                    "The release date of %s cannot be before its issue date.",
                    guarantee.name))

    @api.constrains("amount")
    def _check_amount(self):
        for guarantee in self:
            if guarantee.amount <= 0:
                raise ValidationError(_(
                    "The amount of %s must be above zero.", guarantee.name))

    def action_activate(self):
        for guarantee in self:
            if guarantee.state != "draft":
                raise UserError(_("Only a draft guarantee can be activated."))
            guarantee.state = "active"
            guarantee.message_post(body=_("Guarantee activated."))
        return True

    def action_release(self):
        for guarantee in self:
            if guarantee.state != "active":
                raise UserError(_("Only an active guarantee can be released."))
            guarantee.write({
                "state": "released",
                "release_date": fields.Date.context_today(guarantee),
            })
            guarantee.message_post(body=_("Guarantee released."))
        return True

    def action_cancel(self):
        for guarantee in self:
            if guarantee.state not in ("draft", "active"):
                raise UserError(_(
                    "Only a draft or active guarantee can be cancelled."))
            guarantee.state = "cancelled"
            guarantee.message_post(body=_("Guarantee cancelled."))
        return True
