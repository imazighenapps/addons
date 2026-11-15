# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class VolunteerHours(models.Model):
    _name = "volunteer.hours"
    _description = "Volunteer Hours Entry"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date desc, id desc"

    name = fields.Char(
        default=lambda self: _("New"), copy=False, readonly=True, index=True)
    volunteer_id = fields.Many2one(
        "res.partner", string="Volunteer", required=True, index=True, tracking=True)
    date = fields.Date(
        required=True, default=fields.Date.context_today, tracking=True)
    hours = fields.Float(string="Hours", required=True, tracking=True)
    activity = fields.Char(string="Activity", required=True, tracking=True)
    note = fields.Text()
    state = fields.Selection(
        [("draft", "Draft"), ("submitted", "Submitted"), ("validated", "Validated")],
        default="draft", required=True, tracking=True, index=True)
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True,
        index=True)

    @api.constrains("hours")
    def _check_hours(self):
        for rec in self:
            if rec.hours <= 0:
                raise ValidationError(_("Hours must be strictly positive."))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                seq = self.env["ir.sequence"].next_by_code("volunteer.hours")
                vals["name"] = seq or _("New")
                if vals.get("name", _("New")) == _("New"):
                    vals["name"] = self.env["ir.sequence"].sudo().create({
                        "name": "Volunteer Hours",
                        "code": "volunteer.hours",
                        "prefix": "VOL/%(year)s/",
                        "padding": 4,
                    }).next_by_id()
        return super().create(vals_list)

    def action_submit(self):
        for rec in self:
            if rec.state != "draft":
                raise UserError(_("Only a draft entry can be submitted."))
            rec.state = "submitted"

    def action_validate(self):
        for rec in self:
            if rec.state != "submitted":
                raise UserError(_("Only a submitted entry can be validated."))
            rec.state = "validated"

    def action_reset(self):
        for rec in self:
            rec.state = "draft"
