# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class FreightTariff(models.Model):
    _name = "freight.tariff"
    _description = "Freight Tariff"
    _inherit = ["mail.thread"]
    _order = "carrier_name, lane"

    name = fields.Char(
        required=True, tracking=True,
        help="Reference of the negotiated freight tariff.")
    carrier_name = fields.Char(
        string="Carrier", required=True, tracking=True,
        help="Carrier or transport provider covered by the tariff.")
    lane = fields.Char(
        required=True,
        help="Route or lane the tariff applies to.")
    agreed_amount = fields.Monetary(
        string="Agreed Amount", currency_field="currency_id",
        required=True, tracking=True,
        help="Negotiated freight amount for this lane.")
    currency_id = fields.Many2one(
        "res.currency", required=True,
        default=lambda self: self.env.company.currency_id)
    line_ids = fields.One2many(
        "freight.bill.line", "tariff_id", string="Bill Lines")
    line_count = fields.Integer(
        string="Bill Lines", compute="_compute_line_count", store=True)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)
    note = fields.Text()

    @api.depends("line_ids")
    def _compute_line_count(self):
        for rec in self:
            rec.line_count = len(rec.line_ids)

    @api.constrains("agreed_amount")
    def _check_agreed_amount(self):
        for rec in self:
            if rec.agreed_amount < 0:
                raise ValidationError(_(
                    "The agreed amount of %s cannot be negative.",
                    rec.name))
