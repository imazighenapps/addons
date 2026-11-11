# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class DevdDeviation(models.Model):
    _name = "devd.deviation"
    _description = "Production Deviation"
    _inherit = ["mail.thread"]
    _order = "detected_on desc, id desc"

    name = fields.Char(
        required=True, copy=False, tracking=True,
        default=lambda self: _("New"),
        help="Reference of the deviation record.")
    product_ref = fields.Char(
        string="Product", tracking=True,
        help="Product or batch affected by the deviation.")
    area = fields.Char(
        string="Area", tracking=True,
        help="Line, room or area where the deviation was detected.")
    owner_id = fields.Many2one(
        "res.users", string="Owner", tracking=True,
        default=lambda self: self.env.user,
        help="Person responsible for driving the deviation to closure.")
    detected_on = fields.Date(
        string="Detected On", required=True,
        default=fields.Date.context_today, tracking=True)
    description = fields.Text(
        string="Description",
        help="What happened and how the deviation was noticed.")
    state = fields.Selection(
        [("draft", "Draft"),
         ("investigation", "In Investigation"),
         ("approved", "Approved"),
         ("closed", "Closed")],
        default="draft", required=True, tracking=True, index=True,
        copy=False)
    impact_ids = fields.One2many(
        "devd.impact", "deviation_id", string="Impact Reviews")
    approval_ids = fields.One2many(
        "devd.approval", "deviation_id", string="Approvals")
    impact_count = fields.Integer(
        string="Impact Reviews", compute="_compute_counts", store=True)
    approval_count = fields.Integer(
        string="Approvals", compute="_compute_counts", store=True)
    granted_approval_count = fields.Integer(
        string="Granted Approvals", compute="_compute_counts", store=True)
    closed_on = fields.Date(string="Closed On", readonly=True, copy=False)
    company_id = fields.Many2one(
        "res.company", required=True, index=True,
        default=lambda self: self.env.company)
    note = fields.Text()

    @api.depends("impact_ids", "approval_ids", "approval_ids.decision")
    def _compute_counts(self):
        for rec in self:
            rec.impact_count = len(rec.impact_ids)
            rec.approval_count = len(rec.approval_ids)
            rec.granted_approval_count = len(
                rec.approval_ids.filtered(lambda a: a.decision == "granted"))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "devd.deviation") or _("DEV-%s") % fields.Date.context_today(
                    self).strftime("%Y%m%d")
        return super().create(vals_list)

    @api.constrains("closed_on", "detected_on")
    def _check_dates(self):
        for rec in self:
            if rec.closed_on and rec.detected_on and rec.closed_on < rec.detected_on:
                raise ValidationError(_(
                    "The deviation %s cannot be closed before it was detected.",
                    rec.name))

    def action_investigate(self):
        for rec in self:
            if rec.state != "draft":
                raise ValidationError(_(
                    "Only a draft deviation can move to investigation."))
            rec.state = "investigation"
            rec.message_post(body=_("Deviation moved to investigation."))
        return True

    def action_mark_approved(self):
        for rec in self:
            if rec.state != "investigation":
                raise ValidationError(_(
                    "Only an investigated deviation can be marked approved."))
            if rec.granted_approval_count == 0:
                raise ValidationError(_(
                    "Deviation %s needs at least one granted approval before "
                    "it can be marked approved.", rec.name))
            rec.state = "approved"
            rec.message_post(body=_("Deviation marked as approved."))
        return True

    def action_close(self):
        for rec in self:
            if rec.state != "approved":
                raise ValidationError(_(
                    "Only an approved deviation can be closed."))
            rec.write({
                "state": "closed",
                "closed_on": fields.Date.context_today(rec),
            })
            rec.message_post(body=_("Deviation closed."))
        return True

    def action_reset(self):
        for rec in self:
            if rec.state == "closed":
                raise ValidationError(_(
                    "A closed deviation cannot be reopened."))
            rec.state = "draft"
            rec.message_post(body=_("Deviation reset to draft."))
        return True
