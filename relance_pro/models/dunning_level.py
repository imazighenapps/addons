# -*- coding: utf-8 -*-
from odoo import fields, models


class DunningLevel(models.Model):
    _name = "dunning.level"
    _description = "Dunning Level"
    _order = "sequence, day_offset"

    name = fields.Char(required=True)
    sequence = fields.Integer(default=10)
    company_id = fields.Many2one(
        "res.company", required=True,
        default=lambda self: self.env.company)
    currency_id = fields.Many2one(
        related="company_id.currency_id", store=True, readonly=True)
    day_offset = fields.Integer(
        required=True,
        help="Days after the due date at which this level applies.")
    template_id = fields.Many2one(
        "mail.template", string="Email Template", required=True)
    fee_amount = fields.Monetary(
        string="Late Fee", currency_field="currency_id",
        help="Fee recorded on each dunning line of this level.")
    fee_product_id = fields.Many2one(
        "product.product", string="Fee Product",
        help="Optional product used when the fee is invoiced separately.")
    active = fields.Boolean(default=True)
    note = fields.Text()

    _company_offset_uniq = models.Constraint(
        "unique(company_id, day_offset)",
        "A dunning level already exists at this day offset.")
