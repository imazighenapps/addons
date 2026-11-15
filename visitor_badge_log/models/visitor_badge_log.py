# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class VisitorBadge(models.Model):
    _name = "visitor.badge"
    _description = "Visitor Badge"
    _order = "name, id"

    name = fields.Char(string="Badge ID", required=True)
    active = fields.Boolean(default=True)
    note = fields.Text()
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True,
        index=True)

    _name_company_uniq = models.Constraint(
        "UNIQUE(name, company_id)",
        "A badge with this identifier already exists for this company.")


class VisitorBadgeIssuance(models.Model):
    _name = "visitor.badge.issuance"
    _description = "Visitor Badge Issuance"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "issue_time desc, id desc"

    name = fields.Char(
        default=lambda self: _("New"), copy=False, readonly=True, index=True)
    badge_id = fields.Many2one(
        "visitor.badge", string="Badge", required=True, index=True, tracking=True)
    visitor_name = fields.Char(string="Visitor Name", required=True, tracking=True)
    visitor_company = fields.Char(string="Visitor Company")
    host_id = fields.Many2one("hr.employee", string="Host", tracking=True)
    issue_time = fields.Datetime(
        string="Issue Time", required=True, default=fields.Datetime.now, tracking=True)
    return_time = fields.Datetime(string="Return Time", tracking=True)
    state = fields.Selection(
        [("issued", "Issued"), ("returned", "Returned"), ("lost", "Lost")],
        default="issued", required=True, tracking=True, index=True)
    note = fields.Text()
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True,
        index=True)

    @api.constrains("issue_time", "return_time")
    def _check_times(self):
        for rec in self:
            if rec.issue_time and rec.return_time and rec.return_time < rec.issue_time:
                raise ValidationError(_("Return time cannot be before issue time."))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                seq = self.env["ir.sequence"].next_by_code("visitor.badge.issuance")
                vals["name"] = seq or _("New")
                if vals.get("name", _("New")) == _("New"):
                    vals["name"] = self.env["ir.sequence"].sudo().create({
                        "name": "Visitor Badge Issuance",
                        "code": "visitor.badge.issuance",
                        "prefix": "VB/%(year)s/",
                        "padding": 4,
                    }).next_by_id()
        return super().create(vals_list)

    def action_return(self):
        for rec in self:
            if rec.state != "issued":
                raise UserError(_("Only an issued badge can be returned."))
            rec.write({
                "state": "returned",
                "return_time": rec.return_time or fields.Datetime.now(),
            })

    def action_lost(self):
        for rec in self:
            if rec.state != "issued":
                raise UserError(_("Only an issued badge can be marked lost."))
            rec.state = "lost"

    def action_reset(self):
        for rec in self:
            if rec.state == "issued":
                raise UserError(_("An issued record cannot be reset."))
            rec.write({"state": "issued", "return_time": False})
