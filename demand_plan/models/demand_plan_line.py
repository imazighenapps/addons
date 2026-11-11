# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class DemandPlanLine(models.Model):
    _name = "demand.plan.line"
    _description = "Sales Forecast Line"
    _order = "id"

    plan_id = fields.Many2one(
        "demand.plan", required=True, ondelete="cascade", index=True)
    product_name = fields.Char(
        string="Product", required=True,
        help="Name of the product covered by this forecast line.")
    forecast_qty = fields.Float(
        string="Forecast Qty", default=1.0, required=True)
    actual_qty = fields.Float(string="Actual Qty", default=0.0)
    variance_qty = fields.Float(
        string="Variance Qty", compute="_compute_variance", store=True)
    forecast_amount = fields.Monetary(
        string="Forecast Amount", currency_field="currency_id",
        default=0.0)
    actual_amount = fields.Monetary(
        string="Actual Amount", currency_field="currency_id",
        default=0.0)
    variance_amount = fields.Monetary(
        string="Variance Amount", compute="_compute_variance",
        store=True, currency_field="currency_id")
    currency_id = fields.Many2one(
        related="plan_id.currency_id", store=True, readonly=True)
    company_id = fields.Many2one(
        related="plan_id.company_id", store=True, readonly=True, index=True)

    @api.depends("forecast_qty", "actual_qty",
                 "forecast_amount", "actual_amount")
    def _compute_variance(self):
        for line in self:
            line.variance_qty = line.actual_qty - line.forecast_qty
            line.variance_amount = line.actual_amount - line.forecast_amount

    @api.constrains("forecast_qty")
    def _check_forecast_qty(self):
        for line in self:
            if line.forecast_qty <= 0:
                raise ValidationError(_(
                    "The forecast quantity of %s must be above zero.",
                    line.product_name or _("this line")))
