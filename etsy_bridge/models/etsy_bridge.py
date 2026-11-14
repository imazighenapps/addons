# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class EtsyConnection(models.Model):
    _name = "etsy.connection"
    _description = "Etsy Connection"

    name = fields.Char(required=True)
    company_id = fields.Many2one("res.company", required=True, default=lambda self: self.env.company)
    shop_name = fields.Char()
    api_key_ref = fields.Char(string="API Key Reference")
    state = fields.Selection([("draft", "Draft"), ("active", "Active")], default="draft")
    active = fields.Boolean(default=True)

    def action_activate(self):
        for rec in self:
            if not rec.shop_name:
                raise UserError(_("Set the shop name before activating."))
            rec.state = "active"
        return True


class EtsyListing(models.Model):
    _name = "etsy.listing"
    _description = "Etsy Listing"

    name = fields.Char(required=True)
    connection_id = fields.Many2one("etsy.connection", required=True, ondelete="cascade")
    company_id = fields.Many2one(related="connection_id.company_id", store=True)
    external_id = fields.Char(string="Etsy Listing ID")
    sku = fields.Char()
    price = fields.Monetary(currency_field="currency_id")
    currency_id = fields.Many2one("res.currency", default=lambda self: self.env.company.currency_id)
    stock_qty = fields.Integer(string="Stock Qty")
    state = fields.Selection([("draft", "Draft"), ("active", "Active"), ("inactive", "Inactive")], default="draft")

    @api.constrains("price", "stock_qty")
    def _check_vals(self):
        for rec in self:
            if rec.price < 0 or rec.stock_qty < 0:
                raise ValidationError(_("Price and stock quantity cannot be negative."))

    def action_activate(self):
        for rec in self: rec.state = "active"
        return True

    def action_deactivate(self):
        for rec in self: rec.state = "inactive"
        return True


class EtsyOrder(models.Model):
    _name = "etsy.order"
    _description = "Etsy Order"
    _inherit = ["mail.thread"]
    _order = "order_date desc, id desc"

    name = fields.Char(required=True, copy=False, default="New")
    connection_id = fields.Many2one("etsy.connection", required=True, ondelete="cascade")
    company_id = fields.Many2one(related="connection_id.company_id", store=True)
    external_order_id = fields.Char(string="Etsy Order ID")
    buyer_name = fields.Char()
    order_date = fields.Datetime()
    amount_total = fields.Monetary(currency_field="currency_id")
    currency_id = fields.Many2one("res.currency", default=lambda self: self.env.company.currency_id)
    tracking_number = fields.Char()
    state = fields.Selection(
        [("new", "New"), ("processing", "Processing"), ("shipped", "Shipped"), ("canceled", "Canceled")],
        default="new", required=True, tracking=True)
    note = fields.Text()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("etsy.order") or "ETSY"
        return super().create(vals_list)

    @api.constrains("amount_total")
    def _check_amount(self):
        for rec in self:
            if rec.amount_total < 0:
                raise ValidationError(_("Amount cannot be negative."))

    def action_process(self):
        for rec in self:
            if rec.state != "new":
                raise UserError(_("Only new orders can be processed."))
            rec.state = "processing"
        return True

    def action_ship(self):
        for rec in self:
            if rec.state != "processing":
                raise UserError(_("Process the order before shipping."))
            rec.state = "shipped"
        return True

    def action_cancel(self):
        for rec in self:
            if rec.state == "shipped":
                raise UserError(_("Shipped orders cannot be canceled."))
            rec.state = "canceled"
        return True

    def action_reset(self):
        for rec in self:
            if rec.state == "shipped":
                raise UserError(_("Shipped orders cannot be reset."))
            rec.state = "new"
        return True
