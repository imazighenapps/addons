# -*- coding: utf-8 -*-
from odoo import fields, models


class VendorCatalogItem(models.Model):
    _name = "vendor.catalog.item"
    _description = "Vendor Catalog Item"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "partner_id, product_id, id desc"

    name = fields.Char(string="Catalog Reference", compute="_compute_name", store=True)
    company_id = fields.Many2one("res.company", required=True, default=lambda self: self.env.company, index=True)
    currency_id = fields.Many2one(related="company_id.currency_id", store=True)
    partner_id = fields.Many2one("res.partner", string="Vendor", required=True, tracking=True, domain="[('supplier_rank','>',0)]")
    product_id = fields.Many2one("product.product", string="Product", required=True, tracking=True)
    vendor_code = fields.Char(string="Vendor Product Code")
    price = fields.Monetary(string="Vendor Price", currency_field="currency_id", tracking=True)
    lead_time_days = fields.Integer(string="Lead Time (Days)", tracking=True)
    min_qty = fields.Float(string="Minimum Quantity", default=1.0)
    valid_from = fields.Date(string="Valid From")
    valid_to = fields.Date(string="Valid To")
    active = fields.Boolean(default=True)
    state = fields.Selection([
        ("draft", "Draft"),
        ("active", "Active"),
        ("archived", "Archived"),
    ], default="draft", tracking=True)
    note = fields.Text(string="Notes")

    _sql_constraints = [
        ("vendor_product_uniq", "unique(partner_id, product_id, company_id, vendor_code)",
         "This vendor catalog item already exists for the selected product and vendor code."),
    ]

    def _compute_name(self):
        for rec in self:
            parts = [rec.partner_id.display_name or "", rec.product_id.display_name or ""]
            rec.name = " / ".join([p for p in parts if p]) or "Catalog Item"

    def action_activate(self):
        self.write({"state": "active", "active": True})

    def action_archive_item(self):
        self.write({"state": "archived", "active": False})

    def action_reset_to_draft(self):
        self.write({"state": "draft", "active": True})
