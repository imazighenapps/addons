# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class ContractorCheckin(models.Model):
    _name = "contractor.checkin"
    _description = "Contractor Check-in"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "checkin_time desc, id desc"

    name = fields.Char(
        default=lambda self: _("New"), copy=False, readonly=True, index=True)
    contractor_name = fields.Char(string="Contractor Name", required=True, tracking=True)
    contractor_company = fields.Char(string="Company", tracking=True)
    host_id = fields.Many2one("hr.employee", string="Host", tracking=True)
    purpose = fields.Char(string="Purpose", required=True, tracking=True)
    checkin_time = fields.Datetime(
        string="Check-in Time", required=True, default=fields.Datetime.now, tracking=True)
    checkout_time = fields.Datetime(string="Check-out Time", tracking=True)
    badge_ref = fields.Char(string="Badge / Reference")
    state = fields.Selection(
        [("on_site", "On Site"), ("checked_out", "Checked Out"), ("cancelled", "Cancelled")],
        default="on_site", required=True, tracking=True, index=True)
    note = fields.Text()
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True,
        index=True)

    @api.constrains("checkin_time", "checkout_time")
    def _check_times(self):
        for rec in self:
            if rec.checkin_time and rec.checkout_time and rec.checkout_time < rec.checkin_time:
                raise ValidationError(_("Check-out time cannot be before check-in time."))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                seq = self.env["ir.sequence"].next_by_code("contractor.checkin")
                vals["name"] = seq or _("New")
                if vals.get("name", _("New")) == _("New"):
                    vals["name"] = self.env["ir.sequence"].sudo().create({
                        "name": "Contractor Check-in",
                        "code": "contractor.checkin",
                        "prefix": "CHK/%(year)s/",
                        "padding": 4,
                    }).next_by_id()
        return super().create(vals_list)

    def action_checkout(self):
        for rec in self:
            if rec.state != "on_site":
                raise UserError(_("Only an on-site record can be checked out."))
            rec.write({
                "state": "checked_out",
                "checkout_time": rec.checkout_time or fields.Datetime.now(),
            })

    def action_cancel(self):
        for rec in self:
            if rec.state == "checked_out":
                raise UserError(_("A checked-out record cannot be cancelled."))
            rec.state = "cancelled"

    def action_reset(self):
        for rec in self:
            rec.write({"state": "on_site", "checkout_time": False})
