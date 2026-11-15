# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class SupplierVisitLog(models.Model):
    _name = "supplier.visit.log"
    _description = "Supplier Visit Log"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date desc, id desc"

    name = fields.Char(
        default=lambda self: _("New"), copy=False, readonly=True, index=True)
    partner_id = fields.Many2one(
        "res.partner", string="Supplier", required=True, index=True, tracking=True,
        domain="[('supplier_rank','>',0)]")
    user_id = fields.Many2one(
        "res.users", string="Responsible", default=lambda self: self.env.user,
        required=True, tracking=True)
    date = fields.Date(
        required=True, default=fields.Date.context_today, tracking=True)
    purpose = fields.Char(string="Purpose", required=True, tracking=True)
    attendees = fields.Char(string="Attendees")
    findings = fields.Text(string="Findings")
    followup_action = fields.Text(string="Follow-up Actions")
    followup_date = fields.Date(string="Follow-up Date")
    state = fields.Selection(
        [("draft", "Draft"), ("submitted", "Submitted"), ("reviewed", "Reviewed")],
        default="draft", required=True, tracking=True, index=True)
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True,
        index=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                seq = self.env["ir.sequence"].next_by_code("supplier.visit.log")
                vals["name"] = seq or _("New")
                if vals.get("name", _("New")) == _("New"):
                    vals["name"] = self.env["ir.sequence"].sudo().create({
                        "name": "Supplier Visit Log",
                        "code": "supplier.visit.log",
                        "prefix": "SVL/%(year)s/",
                        "padding": 4,
                    }).next_by_id()
        return super().create(vals_list)

    def action_submit(self):
        for rec in self:
            if rec.state != "draft":
                raise UserError(_("Only a draft report can be submitted."))
            rec.state = "submitted"

    def action_review(self):
        for rec in self:
            if rec.state != "submitted":
                raise UserError(_("Only a submitted report can be reviewed."))
            rec.state = "reviewed"

    def action_reset(self):
        for rec in self:
            rec.state = "draft"
