# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class RebateAccrual(models.Model):
    _name = "rebate.accrual"
    _description = "Rebate Accrual"
    _inherit = ["mail.thread"]
    _order = "accrual_date desc, id desc"

    name = fields.Char(
        required=True,
        default=lambda self: _("Accrual %s") % fields.Date.context_today(self))
    contract_id = fields.Many2one(
        "rebate.contract", string="Contract", required=True,
        ondelete="cascade", index=True, tracking=True)
    partner_id = fields.Many2one(
        related="contract_id.partner_id", store=True, readonly=True)
    accrual_date = fields.Date(
        required=True, default=fields.Date.context_today, tracking=True)
    invoice_ref = fields.Char(
        string="Invoice Reference",
        help="Customer invoice or period reference feeding this accrual.")
    amount = fields.Monetary(
        required=True, currency_field="currency_id", tracking=True)
    currency_id = fields.Many2one(
        related="contract_id.currency_id", store=True, readonly=True)
    state = fields.Selection(
        [("open", "Open"), ("settled", "Settled")],
        default="open", required=True, tracking=True, index=True)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)
    note = fields.Text()

    @api.constrains("amount")
    def _check_amount(self):
        for line in self:
            if line.amount <= 0:
                raise ValidationError(_(
                    "The accrual amount on %s must be above zero.", line.name))

    @api.constrains("accrual_date", "contract_id")
    def _check_accrual_date(self):
        for line in self:
            contract = line.contract_id
            if contract and line.accrual_date:
                if line.accrual_date < contract.date_start \
                        or line.accrual_date > contract.date_end:
                    raise ValidationError(_(
                        "The accrual date of %s must fall within the contract "
                        "period.", line.name))
