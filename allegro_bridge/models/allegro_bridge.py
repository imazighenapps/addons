# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class AllegroConnection(models.Model):
    _name = "allegro.connection"
    _description = "Allegro Connection"

    name = fields.Char(required=True)
    company_id = fields.Many2one("res.company", required=True, default=lambda self: self.env.company)
    account_login = fields.Char()
    token_ref = fields.Char(string="Token Reference")
    environment = fields.Selection([("sandbox", "Sandbox"), ("production", "Production")], default="sandbox", required=True)
    state = fields.Selection([("draft", "Draft"), ("active", "Active")], default="draft")
    active = fields.Boolean(default=True)

    def action_activate(self):
        for rec in self:
            if not rec.account_login:
                raise UserError(_("Set the account login before activating."))
            rec.state = "active"
        return True


class AllegroOffer(models.Model):
    _name = "allegro.offer"
    _description = "Allegro Offer"

    name = fields.Char(required=True)
    connection_id = fields.Many2one("allegro.connection", required=True, ondelete="cascade")
    company_id = fields.Many2one(related="connection_id.company_id", store=True)
    external_id = fields.Char(string="Offer ID")
    price = fields.Monetary(currency_field="currency_id")
    currency_id = fields.Many2one("res.currency", default=lambda self: self.env.company.currency_id)
    stock_qty = fields.Integer()
    state = fields.Selection([("draft", "Draft"), ("active", "Active"), ("ended", "Ended")], default="draft")

    @api.constrains("price", "stock_qty")
    def _check_vals(self):
        for rec in self:
            if rec.price < 0 or rec.stock_qty < 0:
                raise ValidationError(_("Price and stock cannot be negative."))

    def action_activate(self):
        for rec in self: rec.state = "active"
        return True

    def action_end(self):
        for rec in self: rec.state = "ended"
        return True


class AllegroOrder(models.Model):
    _name = "allegro.order"
    _description = "Allegro Order"
    _inherit = ["mail.thread"]
    _order = "order_date desc, id desc"

    name = fields.Char(required=True, copy=False, default="New")
    connection_id = fields.Many2one("allegro.connection", required=True, ondelete="cascade")
    company_id = fields.Many2one(related="connection_id.company_id", store=True)
    external_order_id = fields.Char(string="Allegro Order ID")
    buyer_login = fields.Char()
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
                vals["name"] = self.env["ir.sequence"].next_by_code("allegro.order") or "ALG"
        return super().create(vals_list)

    @api.constrains("amount_total")
    def _check_amount(self):
        for rec in self:
            if rec.amount_total < 0:
                raise ValidationError(_("Amount cannot be negative."))

    def action_process(self):
        for rec in self:
            if rec.state != "new": raise UserError(_("Only new orders can be processed."))
            rec.state = "processing"
        return True

    def action_ship(self):
        for rec in self:
            if rec.state != "processing": raise UserError(_("Process the order before shipping."))
            rec.state = "shipped"
        return True

    def action_cancel(self):
        for rec in self:
            if rec.state == "shipped": raise UserError(_("Shipped orders cannot be canceled."))
            rec.state = "canceled"
        return True

    def action_reset(self):
        for rec in self:
            if rec.state == "shipped": raise UserError(_("Shipped orders cannot be reset."))
            rec.state = "new"
        return True
