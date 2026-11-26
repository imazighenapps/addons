# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class Stock3plContract(models.Model):
    _name = "stock.3pl.contract"
    _description = "3PL Contract"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "id desc"

    name = fields.Char(string="Contract Reference", required=True, copy=False, default="New", tracking=True)
    company_id = fields.Many2one("res.company", required=True, default=lambda self: self.env.company, index=True)
    partner_id = fields.Many2one("res.partner", string="Customer", required=True, tracking=True)
    warehouse_id = fields.Many2one("stock.warehouse", string="Warehouse", required=True, tracking=True)
    currency_id = fields.Many2one(related="company_id.currency_id", store=True)
    date_start = fields.Date(string="Start Date", required=True, tracking=True)
    date_end = fields.Date(string="End Date", tracking=True)
    storage_fee = fields.Monetary(string="Storage Fee / Pallet", currency_field="currency_id")
    handling_fee = fields.Monetary(string="Handling Fee / Operation", currency_field="currency_id")
    inbound_fee = fields.Monetary(string="Inbound Fee / Receipt", currency_field="currency_id")
    outbound_fee = fields.Monetary(string="Outbound Fee / Delivery", currency_field="currency_id")
    state = fields.Selection([
        ("draft", "Draft"),
        ("active", "Active"),
        ("expired", "Expired"),
        ("cancelled", "Cancelled"),
    ], default="draft", tracking=True, required=True)
    statement_ids = fields.One2many("stock.3pl.statement", "contract_id", string="Statements")
    statement_count = fields.Integer(compute="_compute_statement_count")
    note = fields.Text(string="Terms and Notes")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("stock.3pl.contract") or _("New")
        return super().create(vals_list)

    @api.depends("statement_ids")
    def _compute_statement_count(self):
        for rec in self:
            rec.statement_count = len(rec.statement_ids)

    def action_activate(self):
        self.filtered(lambda r: r.state == "draft").write({"state": "active"})

    def action_cancel(self):
        self.filtered(lambda r: r.state in ("draft", "active")).write({"state": "cancelled"})

    def action_reset_to_draft(self):
        self.filtered(lambda r: r.state in ("cancelled", "expired")).write({"state": "draft"})

    def action_view_statements(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("stock_3pl_operations.action_stock_3pl_statement")
        action["domain"] = [("contract_id", "=", self.id)]
        action["context"] = {"default_contract_id": self.id, "default_partner_id": self.partner_id.id}
        return action
