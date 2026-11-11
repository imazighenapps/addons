# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class DualSupplier(models.Model):
    _name = "dual.supplier"
    _description = "Product Supplier Source"
    _order = "role, supplier_name"

    product_id = fields.Many2one(
        "dual.product", string="Product", required=True,
        ondelete="cascade", index=True)
    supplier_name = fields.Char(
        string="Supplier", required=True,
        help="Supplier that can provide the critical product.")
    role = fields.Selection(
        [("primary", "Primary"), ("alternate", "Alternate")],
        default="alternate", required=True,
        help="Whether this supplier is the primary or an alternate source.")
    qualified = fields.Boolean(
        default=False,
        help="Ticked when the supplier is qualified to deliver this product.")
    lead_time_days = fields.Integer(
        string="Lead Time (days)", default=0,
        help="Typical lead time in days for this supplier.")
    company_id = fields.Many2one(
        related="product_id.company_id", store=True, readonly=True,
        index=True)
    note = fields.Char()

    @api.constrains("lead_time_days")
    def _check_lead_time(self):
        for rec in self:
            if rec.lead_time_days < 0:
                raise ValidationError(_(
                    "The lead time of supplier %s cannot be negative.",
                    rec.supplier_name))

    @api.constrains("product_id", "role")
    def _check_product_primary(self):
        for rec in self:
            if not rec.product_id:
                continue
            primaries = rec.product_id.supplier_ids.filtered(
                lambda s: s.role == "primary")
            if len(primaries) != 1:
                raise ValidationError(_(
                    "The product %s must have exactly one primary supplier.",
                    rec.product_id.name))
