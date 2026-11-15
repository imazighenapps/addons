# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

EPS = 1e-6


class DonationLog(models.Model):
    _name = "donation.log"
    _description = "Donation"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date desc, id desc"

    name = fields.Char(
        default=lambda self: _("New"), copy=False, readonly=True, index=True)
    donor_id = fields.Many2one(
        "res.partner", string="Donor", required=True, index=True, tracking=True)
    date = fields.Date(
        required=True, default=fields.Date.context_today, tracking=True)
    amount = fields.Monetary(
        string="Amount", currency_field="currency_id", required=True, tracking=True)
    currency_id = fields.Many2one(
        "res.currency", required=True,
        default=lambda self: self.env.company.currency_id)
    purpose = fields.Char(string="Purpose")
    payment_method = fields.Char(string="Payment Method")
    reference = fields.Char(string="Reference")
    state = fields.Selection(
        [("draft", "Draft"), ("received", "Received"), ("acknowledged", "Acknowledged")],
        default="draft", required=True, tracking=True, index=True)
    note = fields.Text()
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True,
        index=True)

    @api.constrains("amount")
    def _check_amount(self):
        for rec in self:
            if rec.amount <= EPS:
                raise ValidationError(_("Amount must be strictly positive."))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                seq = self.env["ir.sequence"].next_by_code("donation.log")
                vals["name"] = seq or _("New")
                if vals.get("name", _("New")) == _("New"):
                    vals["name"] = self.env["ir.sequence"].sudo().create({
                        "name": "Donation",
                        "code": "donation.log",
                        "prefix": "DON/%(year)s/",
                        "padding": 4,
                    }).next_by_id()
        return super().create(vals_list)

    def action_receive(self):
        for rec in self:
            if rec.state != "draft":
                raise UserError(_("Only a draft donation can be marked received."))
            rec.state = "received"

    def action_acknowledge(self):
        for rec in self:
            if rec.state != "received":
                raise UserError(_("Only a received donation can be acknowledged."))
            rec.state = "acknowledged"

    def action_reset(self):
        for rec in self:
            rec.state = "draft"
