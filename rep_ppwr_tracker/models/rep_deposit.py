# -*- coding: utf-8 -*-
from odoo import api, fields, models


class RepDeposit(models.Model):
    _name = "rep.deposit"
    _description = "Packaging Deposit (consigne)"

    name = fields.Char(required=True)
    amount = fields.Float(string="Deposit Amount (€)", required=True)
    product_id = fields.Many2one("product.product", string="Deposit Product")
    target_rate = fields.Float(string="Target Return Rate (%)", default=90.0)
    packaging_ids = fields.One2many("rep.packaging", "deposit_id")
    units_out = fields.Integer(default=0)
    units_back = fields.Integer(default=0)
    return_rate = fields.Float(compute="_compute_rate", store=True)
    active = fields.Boolean(default=True)

    @api.depends("units_out", "units_back")
    def _compute_rate(self):
        for rec in self:
            rec.return_rate = (100.0 * rec.units_back / rec.units_out) if rec.units_out else 0.0
