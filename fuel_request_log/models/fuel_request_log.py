# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class FuelRequestLog(models.Model):
    _name = "fuel.request.log"
    _description = "Fuel Request"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "request_date desc, id desc"

    name = fields.Char(
        string="Reference", required=True, tracking=True, index=True,
        default=lambda self: _("New"))
    vehicle_id = fields.Many2one(
        "fleet.vehicle", string="Vehicle", required=True, index=True,
        tracking=True)
    requester_id = fields.Many2one(
        "hr.employee", string="Requester", tracking=True)
    request_date = fields.Date(
        required=True, default=fields.Date.context_today, tracking=True)
    amount = fields.Float(string="Requested Amount", required=True, tracking=True)
    currency_id = fields.Many2one(
        "res.currency", default=lambda self: self.env.company.currency_id)
    purpose = fields.Text()
    approver_id = fields.Many2one("res.users", string="Approver", tracking=True)
    user_id = fields.Many2one(
        "res.users", string="Responsible", default=lambda self: self.env.user,
        tracking=True)
    state = fields.Selection(
        [("draft", "Draft"), ("submitted", "Submitted"),
         ("approved", "Approved"), ("fulfilled", "Fulfilled"),
         ("rejected", "Rejected")],
        default="draft", required=True, tracking=True, index=True)
    count = fields.Integer(default=1)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                seq = self.env["ir.sequence"].next_by_code("fuel.request.log")
                vals["name"] = seq or _("New")
        return super().create(vals_list)

    @api.constrains("amount")
    def _check_amount(self):
        for record in self:
            if record.amount <= 0:
                raise ValidationError(_("The requested amount must be positive."))

    def action_submit(self):
        for record in self:
            if record.state != "draft":
                raise UserError(_("Only a draft request can be submitted."))
            record.state = "submitted"
        return True

    def action_approve(self):
        for record in self:
            if record.state != "submitted":
                raise UserError(_("Only a submitted request can be approved."))
            record.write({"state": "approved", "approver_id": self.env.user.id})
        return True

    def action_reject(self):
        for record in self:
            if record.state != "submitted":
                raise UserError(_("Only a submitted request can be rejected."))
            record.state = "rejected"
        return True

    def action_fulfill(self):
        for record in self:
            if record.state != "approved":
                raise UserError(_("Only an approved request can be fulfilled."))
            record.state = "fulfilled"
        return True

    def action_reset_draft(self):
        for record in self:
            if record.state not in ("rejected", "fulfilled"):
                raise UserError(_("Only a rejected or fulfilled request can be reset to draft."))
            record.state = "draft"
        return True
