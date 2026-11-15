# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AssetTransferLog(models.Model):
    _name = "asset.transfer.log"
    _description = "Asset Transfer"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "transfer_date desc, id desc"

    name = fields.Char(
        string="Reference", required=True, tracking=True, index=True,
        default=lambda self: _("New"))
    equipment_id = fields.Many2one(
        "maintenance.equipment", string="Equipment", required=True,
        index=True, tracking=True)
    transfer_date = fields.Date(
        required=True, default=fields.Date.context_today, tracking=True)
    from_employee_id = fields.Many2one(
        "hr.employee", string="From Employee", tracking=True)
    to_employee_id = fields.Many2one(
        "hr.employee", string="To Employee", tracking=True)
    from_location = fields.Char(string="From Location")
    to_location = fields.Char(string="To Location")
    user_id = fields.Many2one(
        "res.users", string="Responsible", default=lambda self: self.env.user,
        tracking=True)
    condition_note = fields.Text(string="Condition / Notes")
    state = fields.Selection(
        [("draft", "Draft"), ("progress", "In Progress"),
         ("done", "Done"), ("cancelled", "Cancelled")],
        default="draft", required=True, tracking=True, index=True)
    count = fields.Integer(default=1)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                seq = self.env["ir.sequence"].next_by_code("asset.transfer.log")
                vals["name"] = seq or _("New")
        return super().create(vals_list)

    def action_start(self):
        for record in self:
            if record.state != "draft":
                raise UserError(_("Only a draft transfer can be started."))
            record.state = "progress"
        return True

    def action_done(self):
        for record in self:
            if record.state != "progress":
                raise UserError(_("Only a transfer in progress can be completed."))
            record.state = "done"
        return True

    def action_cancel(self):
        for record in self:
            if record.state in ("done", "cancelled"):
                raise UserError(_("A done or cancelled transfer cannot be cancelled."))
            record.state = "cancelled"
        return True

    def action_reset_draft(self):
        for record in self:
            if record.state != "cancelled":
                raise UserError(_("Only a cancelled transfer can be reset to draft."))
            record.state = "draft"
        return True
