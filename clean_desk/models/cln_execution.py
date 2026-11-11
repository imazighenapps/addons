# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ClnExecution(models.Model):
    _name = "cln.execution"
    _description = "Cleaning Execution"
    _inherit = ["mail.thread"]
    _order = "scheduled_on desc, id desc"

    name = fields.Char(
        required=True, copy=False, tracking=True,
        default=lambda self: _("New"),
        help="Reference of the cleaning execution.")
    plan_id = fields.Many2one(
        "cln.plan", string="Cleaning Plan", required=True,
        ondelete="cascade", index=True, tracking=True)
    area = fields.Char(
        related="plan_id.area", store=True, readonly=True)
    scheduled_on = fields.Date(
        string="Scheduled On", required=True,
        default=fields.Date.context_today, tracking=True)
    performed_on = fields.Date(
        string="Performed On", tracking=True, copy=False)
    performer_id = fields.Many2one(
        "res.users", string="Performer", tracking=True,
        default=lambda self: self.env.user)
    method_used = fields.Char(
        string="Method Used",
        help="Method or product actually used during cleaning.")
    state = fields.Selection(
        [("planned", "Planned"), ("done", "Done"), ("cancelled", "Cancelled")],
        default="planned", required=True, tracking=True, index=True,
        copy=False)
    company_id = fields.Many2one(
        "res.company", required=True, index=True,
        default=lambda self: self.env.company)
    note = fields.Text()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "cln.execution") or _("CLN-%s") % fields.Date.context_today(
                    self).strftime("%Y%m%d")
        return super().create(vals_list)

    @api.constrains("scheduled_on", "performed_on")
    def _check_dates(self):
        for rec in self:
            if rec.performed_on and rec.scheduled_on \
                    and rec.performed_on < rec.scheduled_on:
                raise ValidationError(_(
                    "Execution %s cannot be performed before it was scheduled.",
                    rec.name))

    def action_done(self):
        for rec in self:
            if rec.state != "planned":
                raise ValidationError(_(
                    "Only a planned execution can be completed."))
            if not rec.performed_on:
                raise ValidationError(_(
                    "Set the performed date before completing %s.", rec.name))
            rec.state = "done"
            rec.message_post(body=_("Cleaning execution completed."))
        return True

    def action_cancel(self):
        for rec in self:
            if rec.state == "done":
                raise ValidationError(_(
                    "A completed execution cannot be cancelled."))
            rec.state = "cancelled"
        return True

    def action_reset(self):
        for rec in self:
            if rec.state == "done":
                raise ValidationError(_(
                    "A completed execution cannot be reset."))
            rec.state = "planned"
        return True
