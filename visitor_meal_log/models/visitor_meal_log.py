# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class VisitorMealLog(models.Model):
    _name = "visitor.meal.log"
    _description = "Visitor Meal"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "meal_date desc, id desc"

    name = fields.Char(
        string="Reference", required=True, tracking=True, index=True,
        default=lambda self: _("New"))
    host_id = fields.Many2one(
        "hr.employee", string="Host / Requester", tracking=True)
    visitor_name = fields.Char(string="Visitor / Guest", tracking=True)
    partner_id = fields.Many2one("res.partner", string="Visitor Company")
    meal_date = fields.Date(
        required=True, default=fields.Date.context_today, tracking=True)
    meal_type = fields.Selection(
        [("breakfast", "Breakfast"), ("lunch", "Lunch"), ("dinner", "Dinner"),
         ("coffee", "Coffee / Snack"), ("other", "Other")],
        default="lunch", required=True, tracking=True)
    meal_count = fields.Integer(string="Number of Meals", default=1, required=True)
    location = fields.Char(string="Location / Meeting")
    user_id = fields.Many2one(
        "res.users", string="Responsible", default=lambda self: self.env.user,
        tracking=True)
    note = fields.Text()
    state = fields.Selection(
        [("draft", "Draft"), ("requested", "Requested"),
         ("served", "Served"), ("cancelled", "Cancelled")],
        default="draft", required=True, tracking=True, index=True)
    count = fields.Integer(default=1)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                seq = self.env["ir.sequence"].next_by_code("visitor.meal.log")
                vals["name"] = seq or _("New")
        return super().create(vals_list)

    @api.constrains("meal_count")
    def _check_meal_count(self):
        for record in self:
            if record.meal_count <= 0:
                raise ValidationError(_("The number of meals must be positive."))

    def action_request(self):
        for record in self:
            if record.state != "draft":
                raise UserError(_("Only a draft meal record can be requested."))
            record.state = "requested"
        return True

    def action_serve(self):
        for record in self:
            if record.state != "requested":
                raise UserError(_("Only a requested meal can be marked served."))
            record.state = "served"
        return True

    def action_cancel(self):
        for record in self:
            if record.state in ("served", "cancelled"):
                raise UserError(_("A served or cancelled meal cannot be cancelled."))
            record.state = "cancelled"
        return True

    def action_reset_draft(self):
        for record in self:
            if record.state != "cancelled":
                raise UserError(_("Only a cancelled meal can be reset to draft."))
            record.state = "draft"
        return True
