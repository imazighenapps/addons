# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class SafetyDrillLog(models.Model):
    _name = "safety.drill.log"
    _description = "Safety Drill"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "drill_date desc, id desc"

    name = fields.Char(
        string="Reference", required=True, tracking=True, index=True,
        default=lambda self: _("New"))
    drill_type = fields.Selection(
        [("fire", "Fire"), ("evacuation", "Evacuation"),
         ("first_aid", "First Aid"), ("spill", "Spill / Chemical"),
         ("other", "Other")],
        string="Drill Type", default="other", required=True, tracking=True)
    planned_date = fields.Date(tracking=True)
    drill_date = fields.Date(
        string="Performed Date", default=fields.Date.context_today, tracking=True)
    location = fields.Char(tracking=True)
    user_id = fields.Many2one(
        "res.users", string="Responsible", default=lambda self: self.env.user,
        tracking=True)
    participant_count = fields.Integer(string="Participants")
    observations = fields.Text()
    corrective_action = fields.Text(string="Corrective Actions")
    state = fields.Selection(
        [("draft", "Draft"), ("done", "Completed"), ("cancelled", "Cancelled")],
        default="draft", required=True, tracking=True, index=True)
    count = fields.Integer(default=1)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                seq = self.env["ir.sequence"].next_by_code("safety.drill.log")
                vals["name"] = seq or _("New")
        return super().create(vals_list)

    def action_done(self):
        for record in self:
            if record.state != "draft":
                raise UserError(_("Only a draft drill can be completed."))
            record.state = "done"
        return True

    def action_cancel(self):
        for record in self:
            if record.state == "cancelled":
                raise UserError(_("This drill is already cancelled."))
            record.state = "cancelled"
        return True

    def action_reset_draft(self):
        for record in self:
            if record.state != "cancelled":
                raise UserError(_("Only a cancelled drill can be reset to draft."))
            record.state = "draft"
        return True
