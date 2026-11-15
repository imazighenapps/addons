# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

EPS = 1e-6


class GiftRegister(models.Model):
    _name = "gift.register"
    _description = "Gift Register Entry"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date desc, id desc"

    name = fields.Char(
        default=lambda self: _("New"), copy=False, readonly=True, index=True)
    direction = fields.Selection(
        [("given", "Given"), ("received", "Received")],
        required=True, default="given", tracking=True)
    counterpart = fields.Char(string="Counterpart / Partner", required=True, tracking=True)
    date = fields.Date(
        required=True, default=fields.Date.context_today, tracking=True)
    employee_id = fields.Many2one(
        "hr.employee", string="Responsible Employee", tracking=True)
    description = fields.Char(string="Gift Description", required=True)
    purpose = fields.Text(string="Purpose / Reason")
    amount = fields.Monetary(
        string="Estimated Value", currency_field="currency_id", tracking=True)
    currency_id = fields.Many2one(
        "res.currency", required=True,
        default=lambda self: self.env.company.currency_id)
    state = fields.Selection(
        [("draft", "Draft"), ("declared", "Declared"), ("approved", "Approved"), ("refused", "Refused")],
        default="draft", required=True, tracking=True, index=True)
    note = fields.Text()
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True,
        index=True)

    @api.constrains("amount")
    def _check_amount(self):
        for rec in self:
            if (rec.amount or 0.0) < -EPS:
                raise ValidationError(_("Estimated value cannot be negative."))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                seq = self.env["ir.sequence"].next_by_code("gift.register")
                vals["name"] = seq or _("New")
                if vals.get("name", _("New")) == _("New"):
                    vals["name"] = self.env["ir.sequence"].sudo().create({
                        "name": "Gift Register",
                        "code": "gift.register",
                        "prefix": "GIFT/%(year)s/",
                        "padding": 4,
                    }).next_by_id()
        return super().create(vals_list)

    def action_declare(self):
        for rec in self:
            if rec.state != "draft":
                raise UserError(_("Only a draft entry can be declared."))
            rec.state = "declared"

    def action_approve(self):
        for rec in self:
            if rec.state != "declared":
                raise UserError(_("Only a declared entry can be approved."))
            rec.state = "approved"

    def action_refuse(self):
        for rec in self:
            if rec.state != "declared":
                raise UserError(_("Only a declared entry can be refused."))
            rec.state = "refused"

    def action_reset(self):
        for rec in self:
            rec.state = "draft"
