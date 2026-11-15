# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ComplaintRegister(models.Model):
    _name = "complaint.register"
    _description = "Complaint Record"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date desc, id desc"

    name = fields.Char(
        default=lambda self: _("New"), copy=False, readonly=True, index=True)
    date = fields.Date(
        required=True, default=fields.Date.context_today, tracking=True)
    source = fields.Char(string="Source / Complainant", required=True, tracking=True)
    contact = fields.Char(string="Contact Details")
    category = fields.Selection(
        [("service", "Service"), ("product", "Product"), ("staff", "Staff"),
         ("facility", "Facility"), ("other", "Other")],
        default="other", required=True, tracking=True)
    severity = fields.Selection(
        [("low", "Low"), ("medium", "Medium"), ("high", "High"), ("critical", "Critical")],
        default="medium", required=True, tracking=True)
    user_id = fields.Many2one(
        "res.users", string="Responsible", tracking=True)
    description = fields.Text(string="Description", required=True)
    resolution = fields.Text(string="Resolution")
    state = fields.Selection(
        [("new", "New"), ("in_progress", "In Progress"), ("resolved", "Resolved"),
         ("closed", "Closed"), ("cancelled", "Cancelled")],
        default="new", required=True, tracking=True, index=True)
    note = fields.Text()
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True,
        index=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                seq = self.env["ir.sequence"].next_by_code("complaint.register")
                vals["name"] = seq or _("New")
                if vals.get("name", _("New")) == _("New"):
                    vals["name"] = self.env["ir.sequence"].sudo().create({
                        "name": "Complaint",
                        "code": "complaint.register",
                        "prefix": "CMP/%(year)s/",
                        "padding": 4,
                    }).next_by_id()
        return super().create(vals_list)

    def action_start(self):
        for rec in self:
            if rec.state != "new":
                raise UserError(_("Only a new complaint can be started."))
            rec.state = "in_progress"

    def action_resolve(self):
        for rec in self:
            if rec.state != "in_progress":
                raise UserError(_("Only a complaint in progress can be resolved."))
            rec.state = "resolved"

    def action_close(self):
        for rec in self:
            if rec.state != "resolved":
                raise UserError(_("Only a resolved complaint can be closed."))
            rec.state = "closed"

    def action_cancel(self):
        for rec in self:
            if rec.state in ("closed", "cancelled"):
                raise UserError(_("This complaint cannot be cancelled."))
            rec.state = "cancelled"

    def action_reset(self):
        for rec in self:
            if rec.state == "new":
                raise UserError(_("This complaint is already new."))
            rec.state = "new"
