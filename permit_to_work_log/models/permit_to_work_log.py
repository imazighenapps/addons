# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class PermitToWorkLog(models.Model):
    _name = "permit.to.work.log"
    _description = "Permit to Work"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "valid_from desc, id desc"

    name = fields.Char(
        string="Reference", required=True, tracking=True, index=True,
        default=lambda self: _("New"))
    permit_type = fields.Selection(
        [("hot_work", "Hot Work"), ("confined_space", "Confined Space"),
         ("work_at_height", "Work at Height"),
         ("electrical", "Electrical"), ("general", "General")],
        required=True, default="general", tracking=True)
    location = fields.Char(required=True, tracking=True)
    contractor_id = fields.Many2one(
        "res.partner", string="Contractor", tracking=True)
    description = fields.Text(required=True)
    safety_measures = fields.Text()
    valid_from = fields.Date(
        required=True, default=fields.Date.context_today, tracking=True)
    valid_to = fields.Date(required=True, tracking=True)
    requester_id = fields.Many2one(
        "res.users", string="Requested By", default=lambda self: self.env.user,
        tracking=True)
    approver_id = fields.Many2one(
        "res.users", string="Approved By", tracking=True)
    state = fields.Selection(
        [("draft", "Draft"), ("requested", "Requested"),
         ("approved", "Approved"), ("active", "Active"),
         ("closed", "Closed"), ("cancelled", "Cancelled")],
        default="draft", required=True, tracking=True, index=True)
    count = fields.Integer(default=1)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                seq = self.env["ir.sequence"].next_by_code("permit.to.work.log")
                vals["name"] = seq or _("New")
        return super().create(vals_list)

    @api.constrains("valid_from", "valid_to")
    def _check_dates(self):
        for record in self:
            if record.valid_from and record.valid_to \
                    and record.valid_to < record.valid_from:
                raise ValidationError(
                    _("The permit end date cannot be before its start date."))

    def action_submit(self):
        for record in self:
            if record.state != "draft":
                raise UserError(_("Only a draft permit can be requested."))
            record.state = "requested"
        return True

    def action_approve(self):
        for record in self:
            if record.state != "requested":
                raise UserError(_("Only a requested permit can be approved."))
            record.write({"state": "approved", "approver_id": self.env.user.id})
        return True

    def action_activate(self):
        for record in self:
            if record.state != "approved":
                raise UserError(_("Only an approved permit can be activated."))
            record.state = "active"
        return True

    def action_close(self):
        for record in self:
            if record.state != "active":
                raise UserError(_("Only an active permit can be closed."))
            record.state = "closed"
        return True

    def action_cancel(self):
        for record in self:
            if record.state in ("closed", "cancelled"):
                raise UserError(
                    _("A closed or cancelled permit cannot be cancelled."))
            record.state = "cancelled"
        return True

    def action_reset_draft(self):
        for record in self:
            if record.state != "cancelled":
                raise UserError(_("Only a cancelled permit can be reset."))
            record.state = "draft"
        return True
