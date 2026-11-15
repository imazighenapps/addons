# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

EPS = 1e-6


class CanteenMealLog(models.Model):
    _name = "canteen.meal.log"
    _description = "Canteen Meal Log"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date desc, id desc"

    name = fields.Char(
        default=lambda self: _("New"), copy=False, readonly=True, index=True)
    date = fields.Date(
        required=True, default=fields.Date.context_today, tracking=True, index=True)
    meal_type = fields.Selection(
        [("breakfast", "Breakfast"), ("lunch", "Lunch"), ("dinner", "Dinner"),
         ("snack", "Snack"), ("other", "Other")],
        default="lunch", required=True, tracking=True)
    headcount = fields.Integer(string="Headcount", required=True, default=0, tracking=True)
    cost = fields.Monetary(
        string="Total Cost", currency_field="currency_id", tracking=True)
    subsidy = fields.Monetary(
        string="Subsidy", currency_field="currency_id", tracking=True)
    currency_id = fields.Many2one(
        "res.currency", required=True,
        default=lambda self: self.env.company.currency_id)
    state = fields.Selection(
        [("draft", "Draft"), ("confirmed", "Confirmed")],
        default="draft", required=True, tracking=True, index=True)
    note = fields.Text()
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True,
        index=True)

    @api.constrains("headcount", "cost", "subsidy")
    def _check_values(self):
        for rec in self:
            if rec.headcount < 0:
                raise ValidationError(_("Headcount cannot be negative."))
            if (rec.cost or 0.0) < -EPS:
                raise ValidationError(_("Cost cannot be negative."))
            if (rec.subsidy or 0.0) < -EPS:
                raise ValidationError(_("Subsidy cannot be negative."))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                seq = self.env["ir.sequence"].next_by_code("canteen.meal.log")
                vals["name"] = seq or _("New")
                if vals.get("name", _("New")) == _("New"):
                    vals["name"] = self.env["ir.sequence"].sudo().create({
                        "name": "Canteen Meal Log",
                        "code": "canteen.meal.log",
                        "prefix": "CAN/%(year)s/",
                        "padding": 4,
                    }).next_by_id()
        return super().create(vals_list)

    def action_confirm(self):
        for rec in self:
            if rec.state != "draft":
                raise UserError(_("Only a draft log can be confirmed."))
            rec.state = "confirmed"

    def action_reset(self):
        for rec in self:
            rec.state = "draft"
