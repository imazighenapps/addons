# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class VendorChargeback(models.Model):
    _name = "vendor.chargeback"
    _description = "Vendor Chargeback"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date desc, id desc"

    name = fields.Char(string="Chargeback Reference", required=True, copy=False, default="New", tracking=True)
    company_id = fields.Many2one("res.company", required=True, default=lambda self: self.env.company, index=True)
    currency_id = fields.Many2one(related="company_id.currency_id", store=True)
    partner_id = fields.Many2one("res.partner", string="Vendor", required=True, tracking=True, domain="[('supplier_rank','>',0)]")
    purchase_id = fields.Many2one("purchase.order", string="Purchase Order")
    invoice_id = fields.Many2one("account.move", string="Vendor Bill", domain="[('move_type','=','in_invoice')]")
    date = fields.Date(string="Date", default=fields.Date.context_today, required=True, tracking=True)
    reason = fields.Selection([
        ("late_delivery", "Late Delivery"),
        ("quality", "Quality Issue"),
        ("shortage", "Shortage"),
        ("pricing", "Pricing Error"),
        ("other", "Other"),
    ], string="Reason", required=True, default="other", tracking=True)
    amount = fields.Monetary(string="Amount", required=True, currency_field="currency_id", tracking=True)
    state = fields.Selection([
        ("draft", "Draft"),
        ("submitted", "Submitted"),
        ("approved", "Approved"),
        ("resolved", "Resolved"),
        ("cancelled", "Cancelled"),
    ], default="draft", tracking=True)
    description = fields.Text(string="Description")
    resolution_note = fields.Text(string="Resolution Note")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("vendor.chargeback") or _("New")
        return super().create(vals_list)

    def action_submit(self):
        self.filtered(lambda r: r.state == "draft").write({"state": "submitted"})

    def action_approve(self):
        self.filtered(lambda r: r.state == "submitted").write({"state": "approved"})

    def action_resolve(self):
        self.filtered(lambda r: r.state in ("submitted", "approved")).write({"state": "resolved"})

    def action_cancel(self):
        self.filtered(lambda r: r.state != "resolved").write({"state": "cancelled"})

    def action_reset_to_draft(self):
        self.filtered(lambda r: r.state == "cancelled").write({"state": "draft"})
