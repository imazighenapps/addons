# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class FreightBillLine(models.Model):
    _name = "freight.bill.line"
    _description = "Freight Bill Line"
    _inherit = ["mail.thread"]
    _order = "bill_date desc, id desc"

    name = fields.Char(
        string="Bill Reference", required=True, tracking=True,
        help="Supplier bill or invoice reference carrying the freight.")
    tariff_id = fields.Many2one(
        "freight.tariff", string="Tariff", required=True,
        ondelete="restrict", tracking=True, index=True)
    carrier_name = fields.Char(
        related="tariff_id.carrier_name", store=True, readonly=True)
    billed_amount = fields.Monetary(
        string="Billed Amount", currency_field="currency_id",
        required=True, tracking=True,
        help="Freight amount actually charged on the supplier bill.")
    currency_id = fields.Many2one(
        "res.currency", required=True,
        default=lambda self: self.env.company.currency_id)
    overcharge_amount = fields.Monetary(
        string="Overcharge", currency_field="currency_id",
        compute="_compute_overcharge", store=True,
        help="Amount billed above the agreed tariff.")
    is_overcharged = fields.Boolean(
        string="Overcharged", compute="_compute_overcharge", store=True,
        help="True when the billed amount exceeds the agreed tariff.")
    bill_date = fields.Date(
        string="Bill Date", required=True, default=fields.Date.context_today,
        tracking=True)
    disputed = fields.Boolean(
        default=False, tracking=True,
        help="Ticked when the overcharge is challenged with the supplier.")
    state = fields.Selection(
        [("draft", "Draft"), ("checked", "Checked"),
         ("disputed", "Disputed")],
        default="draft", required=True, copy=False, tracking=True,
        index=True)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)
    note = fields.Text()

    @api.depends("billed_amount", "tariff_id", "tariff_id.agreed_amount")
    def _compute_overcharge(self):
        for rec in self:
            agreed = rec.tariff_id.agreed_amount if rec.tariff_id else 0.0
            diff = (rec.billed_amount or 0.0) - agreed
            rec.overcharge_amount = diff if diff > 0 else 0.0
            rec.is_overcharged = bool(diff > 0)

    @api.constrains("billed_amount")
    def _check_billed_amount(self):
        for rec in self:
            if rec.billed_amount < 0:
                raise ValidationError(_(
                    "The billed amount of %s cannot be negative.",
                    rec.name))

    def action_check(self):
        for rec in self:
            if rec.state != "draft":
                raise ValidationError(_(
                    "Only draft lines can be checked: %s.", rec.name))
            rec.state = "checked"
            rec.message_post(body=_("The freight line was checked."))
        return True

    def action_dispute(self):
        for rec in self:
            if rec.state == "disputed":
                raise ValidationError(_(
                    "The freight line %s is already disputed.", rec.name))
            if not rec.is_overcharged:
                raise ValidationError(_(
                    "Only overcharged lines can be disputed: %s.",
                    rec.name))
            rec.write({"state": "disputed", "disputed": True})
            rec.message_post(body=_(
                "The overcharge of %s was disputed.", rec.overcharge_amount))
        return True
