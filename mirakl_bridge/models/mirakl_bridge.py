# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class MiraklConnection(models.Model):
    _name = "mirakl.connection"
    _description = "Mirakl Connection"
    _inherit = ["mail.thread"]

    name = fields.Char(required=True)
    company_id = fields.Many2one("res.company", required=True, default=lambda self: self.env.company)
    shop_id = fields.Char(string="Shop ID")
    api_key_ref = fields.Char(string="API Key Reference")
    base_url = fields.Char(default="https://marketplace.example.com/api")
    state = fields.Selection([("draft", "Draft"), ("active", "Active")], default="draft", tracking=True)
    active = fields.Boolean(default=True)

    def action_activate(self):
        for rec in self:
            if not rec.shop_id or not rec.api_key_ref:
                raise UserError(_("Set shop ID and API key reference before activating."))
            rec.state = "active"
        return True


class MiraklOrder(models.Model):
    _name = "mirakl.order"
    _description = "Mirakl Marketplace Order"
    _inherit = ["mail.thread"]
    _order = "order_date desc, id desc"

    name = fields.Char(required=True, copy=False, default="New")
    connection_id = fields.Many2one("mirakl.connection", required=True, ondelete="cascade")
    company_id = fields.Many2one(related="connection_id.company_id", store=True)
    external_order_id = fields.Char(string="Marketplace Order ID", index=True)
    partner_name = fields.Char(string="Customer Name")
    partner_email = fields.Char(string="Customer Email")
    order_date = fields.Datetime()
    amount_total = fields.Monetary(currency_field="currency_id")
    currency_id = fields.Many2one("res.currency", default=lambda self: self.env.company.currency_id, required=True)
    line_summary = fields.Text()
    tracking_number = fields.Char()
    carrier_name = fields.Char()
    state = fields.Selection(
        [("new", "New"), ("accepted", "Accepted"), ("shipped", "Shipped"),
         ("invoiced", "Invoiced"), ("closed", "Closed"), ("error", "Error")],
        default="new", required=True, tracking=True)
    note = fields.Text()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("mirakl.order") or "MRK"
        return super().create(vals_list)

    @api.constrains("amount_total")
    def _check_amount(self):
        for rec in self:
            if rec.amount_total < 0:
                raise ValidationError(_("Amount cannot be negative."))

    def action_accept(self):
        for rec in self:
            if rec.state != "new":
                raise UserError(_("Only new orders can be accepted."))
            rec.state = "accepted"
        return True

    def action_ship(self):
        for rec in self:
            if rec.state != "accepted":
                raise UserError(_("Accept the order before shipping."))
            if not rec.tracking_number:
                raise UserError(_("Set a tracking number before shipping."))
            rec.state = "shipped"
        return True

    def action_invoice(self):
        for rec in self:
            if rec.state != "shipped":
                raise UserError(_("Ship the order before invoicing."))
            rec.state = "invoiced"
        return True

    def action_close(self):
        for rec in self:
            if rec.state != "invoiced":
                raise UserError(_("Invoice the order before closing."))
            rec.state = "closed"
        return True

    def action_reset(self):
        for rec in self:
            if rec.state == "closed":
                raise UserError(_("Closed orders cannot be reset."))
            rec.state = "new"
        return True
