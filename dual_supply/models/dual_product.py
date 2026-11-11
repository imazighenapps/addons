# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class DualProduct(models.Model):
    _name = "dual.product"
    _description = "Critical Sourced Product"
    _inherit = ["mail.thread"]
    _order = "qualified_source_count asc, name"

    name = fields.Char(
        string="Product", required=True, tracking=True,
        help="Critical product whose supply sources are mapped.")
    critical = fields.Boolean(
        default=True, tracking=True,
        help="Ticked when the product is critical for operations.")
    supplier_ids = fields.One2many(
        "dual.supplier", "product_id", string="Suppliers")
    qualified_source_count = fields.Integer(
        string="Qualified Sources", compute="_compute_source_counts",
        store=True,
        help="Number of qualified suppliers for this product.")
    single_source = fields.Boolean(
        string="Single Source", compute="_compute_source_counts",
        store=True,
        help="True when only one qualified supplier is available.")
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)
    note = fields.Text()

    @api.depends("supplier_ids", "supplier_ids.qualified",
                 "supplier_ids.role")
    def _compute_source_counts(self):
        for rec in self:
            qualified = rec.supplier_ids.filtered(lambda s: s.qualified)
            rec.qualified_source_count = len(qualified)
            rec.single_source = bool(rec.qualified_source_count <= 1)

    @api.constrains("supplier_ids", "supplier_ids.role")
    def _check_primary_supplier(self):
        for rec in self:
            primaries = rec.supplier_ids.filtered(
                lambda s: s.role == "primary")
            if rec.supplier_ids and len(primaries) != 1:
                raise ValidationError(_(
                    "The product %s must have exactly one primary supplier.",
                    rec.name))
