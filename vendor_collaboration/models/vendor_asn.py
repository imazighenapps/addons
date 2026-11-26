# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class VendorAsn(models.Model):
    _name = "vendor.asn"
    _description = "Vendor Advanced Shipping Notice"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "expected_date desc, id desc"

    name = fields.Char(string="ASN Reference", required=True, copy=False, default="New", tracking=True)
    company_id = fields.Many2one("res.company", required=True, default=lambda self: self.env.company, index=True)
    partner_id = fields.Many2one("res.partner", string="Vendor", required=True, tracking=True, domain="[('supplier_rank','>',0)]")
    purchase_id = fields.Many2one("purchase.order", string="Purchase Order", tracking=True)
    picking_id = fields.Many2one("stock.picking", string="Receipt", tracking=True)
    expected_date = fields.Date(string="Expected Arrival", required=True, tracking=True)
    carrier_name = fields.Char(string="Carrier")
    tracking_ref = fields.Char(string="Tracking Reference")
    state = fields.Selection([
        ("draft", "Draft"),
        ("submitted", "Submitted"),
        ("received", "Received"),
        ("cancelled", "Cancelled"),
    ], default="draft", tracking=True)
    line_ids = fields.One2many("vendor.asn.line", "asn_id", string="Lines")
    note = fields.Text(string="Notes")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("vendor.asn") or _("New")
        return super().create(vals_list)

    def action_submit(self):
        self.filtered(lambda r: r.state == "draft").write({"state": "submitted"})

    def action_receive(self):
        self.filtered(lambda r: r.state == "submitted").write({"state": "received"})

    def action_cancel(self):
        self.filtered(lambda r: r.state in ("draft", "submitted")).write({"state": "cancelled"})

    def action_reset_to_draft(self):
        self.filtered(lambda r: r.state == "cancelled").write({"state": "draft"})


class VendorAsnLine(models.Model):
    _name = "vendor.asn.line"
    _description = "Vendor ASN Line"

    asn_id = fields.Many2one("vendor.asn", required=True, ondelete="cascade", index=True)
    product_id = fields.Many2one("product.product", string="Product", required=True)
    qty_expected = fields.Float(string="Expected Quantity", required=True, default=1.0)
    qty_received = fields.Float(string="Received Quantity", default=0.0)
    uom_id = fields.Many2one("uom.uom", string="Unit of Measure", related="product_id.uom_id", readonly=True)
