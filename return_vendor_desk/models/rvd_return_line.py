# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class RvdReturnLine(models.Model):
    _name = "rvd.return.line"
    _description = "Vendor Return Line"
    _order = "id"

    return_id = fields.Many2one(
        "rvd.return", string="Return", required=True, ondelete="cascade",
        index=True)
    product_name = fields.Char(
        string="Product", required=True,
        help="Rejected product or item returned to the supplier.")
    quantity = fields.Float(
        default=1.0, required=True,
        help="Quantity of the rejected item sent back.")
    reason = fields.Char(
        string="Rejection Reason",
        help="Why the goods are rejected and returned.")
    company_id = fields.Many2one(
        related="return_id.company_id", store=True, readonly=True,
        index=True)

    @api.constrains("quantity")
    def _check_quantity(self):
        for line in self:
            if line.quantity <= 0:
                raise ValidationError(_(
                    "The quantity of %s must be above zero.",
                    line.product_name))
