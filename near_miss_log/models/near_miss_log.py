# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class NearMissLog(models.Model):
    _name = "near.miss.log"
    _description = "Near Miss Report"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "event_date desc, id desc"

    name = fields.Char(
        string="Reference", required=True, tracking=True, index=True,
        default=lambda self: _("New"))
    event_date = fields.Date(
        required=True, default=fields.Date.context_today, tracking=True)
    location = fields.Char(required=True, tracking=True)
    description = fields.Text(required=True)
    severity = fields.Selection(
        [("low", "Low"), ("medium", "Medium"), ("high", "High")],
        required=True, default="low", tracking=True)
    reporter_id = fields.Many2one(
        "hr.employee", string="Reported By", tracking=True)
    corrective_action = fields.Text()
    responsible_id = fields.Many2one(
        "res.users", string="Action Owner", tracking=True)
    state = fields.Selection(
        [("draft", "Draft"), ("reported", "Reported"),
         ("investigating", "Investigating"), ("closed", "Closed"),
         ("cancelled", "Cancelled")],
        default="draft", required=True, tracking=True, index=True)
    count = fields.Integer(default=1)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                seq = self.env["ir.sequence"].next_by_code("near.miss.log")
                vals["name"] = seq or _("New")
        return super().create(vals_list)

    def action_report(self):
        for record in self:
            if record.state != "draft":
                raise UserError(_("Only a draft report can be submitted."))
            record.state = "reported"
        return True

    def action_investigate(self):
        for record in self:
            if record.state != "reported":
                raise UserError(
                    _("Only a reported near miss can be investigated."))
            if not record.corrective_action:
                raise UserError(
                    _("A corrective action is required before investigating."))
            if not record.responsible_id:
                record.responsible_id = self.env.user.id
            record.state = "investigating"
        return True

    def action_close(self):
        for record in self:
            if record.state != "investigating":
                raise UserError(
                    _("Only an investigated near miss can be closed."))
            record.state = "closed"
        return True

    def action_cancel(self):
        for record in self:
            if record.state in ("closed", "cancelled"):
                raise UserError(
                    _("A closed or cancelled report cannot be cancelled."))
            record.state = "cancelled"
        return True

    def action_reset_draft(self):
        for record in self:
            if record.state != "cancelled":
                raise UserError(_("Only a cancelled report can be reset."))
            record.state = "draft"
        return True
