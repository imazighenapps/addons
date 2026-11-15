# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class StaffAwardLog(models.Model):
    _name = "staff.award.log"
    _description = "Staff Award"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "award_date desc, id desc"

    name = fields.Char(
        string="Reference", required=True, tracking=True, index=True,
        default=lambda self: _("New"))
    employee_id = fields.Many2one(
        "hr.employee", string="Employee", required=True, index=True,
        tracking=True)
    award_type = fields.Selection(
        [("recognition", "Recognition"), ("performance", "Performance"),
         ("teamwork", "Teamwork"), ("innovation", "Innovation"),
         ("service", "Service"), ("other", "Other")],
        default="recognition", required=True, tracking=True)
    award_date = fields.Date(
        required=True, default=fields.Date.context_today, tracking=True)
    awarded_by_id = fields.Many2one(
        "res.users", string="Awarded By", default=lambda self: self.env.user,
        tracking=True)
    value_note = fields.Char(string="Value / Points")
    reason = fields.Text(required=True)
    state = fields.Selection(
        [("draft", "Draft"), ("announced", "Announced"), ("cancelled", "Cancelled")],
        default="draft", required=True, tracking=True, index=True)
    count = fields.Integer(default=1)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                seq = self.env["ir.sequence"].next_by_code("staff.award.log")
                vals["name"] = seq or _("New")
        return super().create(vals_list)

    def action_announce(self):
        for record in self:
            if record.state != "draft":
                raise UserError(_("Only a draft award can be announced."))
            record.state = "announced"
        return True

    def action_cancel(self):
        for record in self:
            if record.state == "cancelled":
                raise UserError(_("This award is already cancelled."))
            record.state = "cancelled"
        return True

    def action_reset_draft(self):
        for record in self:
            if record.state != "cancelled":
                raise UserError(_("Only a cancelled award can be reset to draft."))
            record.state = "draft"
        return True
