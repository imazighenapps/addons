# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class BankGuaranteeRenewal(models.Model):
    _name = "bank.guarantee.renewal"
    _description = "Guarantee Renewal"
    _order = "renewed_on desc, id desc"

    guarantee_id = fields.Many2one(
        "bank.guarantee", string="Guarantee", required=True,
        ondelete="cascade", index=True)
    renewed_on = fields.Date(
        required=True, default=fields.Date.context_today)
    previous_expiry = fields.Date(required=True)
    new_expiry = fields.Date(required=True)
    fee = fields.Monetary(currency_field="currency_id")
    currency_id = fields.Many2one(
        related="guarantee_id.currency_id", store=True, readonly=True)
    note = fields.Char()
    company_id = fields.Many2one(
        related="guarantee_id.company_id", store=True, readonly=True,
        index=True)

    @api.constrains("previous_expiry", "new_expiry")
    def _check_dates(self):
        for renewal in self:
            if renewal.new_expiry <= renewal.previous_expiry:
                raise ValidationError(_(
                    "The new expiry date must be after the previous one."))

    @api.constrains("fee")
    def _check_fee(self):
        for renewal in self:
            if renewal.fee < 0:
                raise ValidationError(_(
                    "The renewal fee cannot be negative."))

    @api.model_create_multi
    def create(self, vals_list):
        renewals = super().create(vals_list)
        for renewal in renewals:
            guarantee = renewal.guarantee_id
            if guarantee.state == "released":
                raise UserError(_(
                    "A released guarantee cannot be renewed."))
            guarantee.expiry_date = renewal.new_expiry
            guarantee.message_post(body=_(
                "Guarantee renewed until %s.", renewal.new_expiry))
        return renewals
