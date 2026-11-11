# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class RmaLine(models.Model):
    _name = "rma.line"
    _description = "Return Line"
    _order = "id"

    request_id = fields.Many2one(
        "rma.request", required=True, ondelete="cascade", index=True)
    product_name = fields.Char(string="Product", required=True)
    quantity = fields.Float(required=True, default=1.0)
    unit_value = fields.Monetary(
        string="Unit Value", currency_field="currency_id", default=0.0)
    subtotal = fields.Monetary(
        compute="_compute_subtotal", store=True,
        currency_field="currency_id")
    currency_id = fields.Many2one(
        related="request_id.currency_id", store=True, readonly=True)
    company_id = fields.Many2one(
        related="request_id.company_id", store=True, readonly=True,
        index=True)
    note = fields.Char()

    @api.depends("quantity", "unit_value")
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.quantity * line.unit_value

    @api.constrains("quantity", "unit_value")
    def _check_values(self):
        for line in self:
            if line.quantity <= 0:
                raise ValidationError(_(
                    "The returned quantity of %s must be above zero.",
                    line.product_name))
            if line.unit_value < 0:
                raise ValidationError(_(
                    "The unit value of %s cannot be negative.",
                    line.product_name))
