# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class PrRequestLine(models.Model):
    _name = "pr.request.line"
    _description = "Purchase Request Line"
    _order = "id"

    request_id = fields.Many2one(
        "pr.request", string="Request", required=True, ondelete="cascade",
        index=True)
    product_name = fields.Char(
        string="Product / Need", required=True,
        help="What the department needs to buy.")
    description = fields.Char(
        help="Extra detail for the buyer, such as brand or specification.")
    quantity = fields.Float(
        default=1.0, required=True, digits="Product Unit of Measure")
    uom_name = fields.Char(
        string="Unit", help="Unit requested, for example pcs, kg or box.")
    needed_on = fields.Date(
        string="Needed On", related="request_id.needed_on", store=True,
        readonly=True)
    company_id = fields.Many2one(
        "res.company", related="request_id.company_id", store=True,
        readonly=True, index=True)

    @api.constrains("quantity")
    def _check_quantity(self):
        for line in self:
            if line.quantity <= 0:
                raise ValidationError(_(
                    "The quantity for %s must be above zero.",
                    line.product_name))
