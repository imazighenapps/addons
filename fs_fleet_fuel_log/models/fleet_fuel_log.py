# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

EPS = 1e-6


class FuelVehicle(models.Model):
    _name = "fuel.vehicle"
    _description = "Fuel Vehicle"
    _order = "name, id"

    name = fields.Char(required=True)
    ref = fields.Char(string="Plate / Reference")
    active = fields.Boolean(default=True)
    note = fields.Text()
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True,
        index=True)

    _sql_constraints = [
        ('name_company_uniq', "UNIQUE(name, company_id)", "A vehicle with this name already exists for this company."),
    ]


class FuelLog(models.Model):
    _name = "fuel.log"
    _description = "Fuel Log Entry"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date desc, id desc"

    name = fields.Char(
        default=lambda self: _("New"), copy=False, readonly=True, index=True)
    vehicle_id = fields.Many2one(
        "fuel.vehicle", string="Vehicle", required=True, index=True, tracking=True)
    driver_id = fields.Many2one(
        "hr.employee", string="Driver", tracking=True)
    date = fields.Date(
        required=True, default=fields.Date.context_today, tracking=True)
    odometer = fields.Float(string="Odometer")
    liter = fields.Float(string="Liters", required=True, tracking=True)
    amount_total = fields.Monetary(
        string="Total Cost", currency_field="currency_id", required=True,
        tracking=True)
    currency_id = fields.Many2one(
        "res.currency", required=True,
        default=lambda self: self.env.company.currency_id)
    price_per_liter = fields.Monetary(
        compute="_compute_price", currency_field="currency_id",
        string="Price / Liter", store=True)
    vendor_ref = fields.Char(string="Station / Reference")
    state = fields.Selection(
        [("draft", "Draft"), ("confirmed", "Confirmed")],
        default="draft", required=True, tracking=True, index=True)
    note = fields.Text()
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True,
        index=True)

    @api.depends("liter", "amount_total")
    def _compute_price(self):
        for rec in self:
            rec.price_per_liter = (rec.amount_total / rec.liter) if rec.liter else 0.0

    @api.constrains("liter", "amount_total", "odometer")
    def _check_values(self):
        for rec in self:
            if rec.liter <= 0:
                raise ValidationError(_("Liters must be strictly positive."))
            if rec.amount_total < -EPS:
                raise ValidationError(_("Total cost cannot be negative."))
            if rec.odometer < -EPS:
                raise ValidationError(_("Odometer cannot be negative."))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                seq = self.env["ir.sequence"].next_by_code("fuel.log")
                vals["name"] = seq or _("New")
                if vals.get("name", _("New")) == _("New"):
                    vals["name"] = self.env["ir.sequence"].sudo().create({
                        "name": "Fuel Log",
                        "code": "fuel.log",
                        "prefix": "FUEL/%(year)s/",
                        "padding": 4,
                    }).next_by_id()
        return super().create(vals_list)

    def action_confirm(self):
        for rec in self:
            if rec.state != "draft":
                raise UserError(_("Only a draft entry can be confirmed."))
            rec.state = "confirmed"

    def action_reset(self):
        for rec in self:
            if rec.state != "confirmed":
                raise UserError(_("Only a confirmed entry can be reset."))
            rec.state = "draft"
