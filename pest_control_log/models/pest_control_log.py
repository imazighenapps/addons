# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class PestControlLog(models.Model):
    _name = "pest.control.log"
    _description = "Pest Control Intervention"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "intervention_date desc, id desc"

    name = fields.Char(
        string="Reference", required=True, tracking=True, index=True,
        default=lambda self: _("New"))
    intervention_date = fields.Date(
        string="Date", required=True, default=fields.Date.context_today,
        tracking=True)
    scheduled_date = fields.Date(tracking=True)
    partner_id = fields.Many2one(
        "res.partner", string="Provider", tracking=True)
    area = fields.Char(string="Area / Location", tracking=True)
    pest_type = fields.Selection(
        [("rodent", "Rodents"), ("insect", "Insects"),
         ("bird", "Birds"), ("termite", "Termites"), ("other", "Other")],
        default="other", tracking=True)
    user_id = fields.Many2one(
        "res.users", string="Responsible", default=lambda self: self.env.user,
        tracking=True)
    findings = fields.Text()
    treatment_note = fields.Text(string="Treatment / Products")
    followup_note = fields.Text(string="Follow-up")
    state = fields.Selection(
        [("draft", "Draft"), ("scheduled", "Scheduled"),
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
                seq = self.env["ir.sequence"].next_by_code("pest.control.log")
                vals["name"] = seq or _("New")
        return super().create(vals_list)

    def action_schedule(self):
        for record in self:
            if record.state != "draft":
                raise UserError(_("Only a draft intervention can be scheduled."))
            record.state = "scheduled"
        return True

    def action_done(self):
        for record in self:
            if record.state != "scheduled":
                raise UserError(_("Only a scheduled intervention can be marked done."))
            record.state = "done"
        return True

    def action_cancel(self):
        for record in self:
            if record.state in ("done", "cancelled"):
                raise UserError(_("A done or cancelled intervention cannot be cancelled."))
            record.state = "cancelled"
        return True

    def action_reset_draft(self):
        for record in self:
            if record.state != "cancelled":
                raise UserError(_("Only a cancelled intervention can be reset to draft."))
            record.state = "draft"
        return True
