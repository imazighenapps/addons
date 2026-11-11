# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ClcCheck(models.Model):
    _name = "clc.check"
    _description = "Line Clearance"
    _inherit = ["mail.thread"]
    _order = "planned_on desc, id desc"

    name = fields.Char(
        required=True, copy=False, tracking=True,
        default=lambda self: _("New"),
        help="Reference of the line clearance.")
    line_area = fields.Char(
        string="Line / Area", required=True, tracking=True,
        help="Production line or area to be cleared.")
    outgoing_product = fields.Char(
        string="Outgoing Product", tracking=True,
        help="Product leaving the line before the changeover.")
    incoming_product = fields.Char(
        string="Incoming Product", tracking=True,
        help="Product scheduled to run after the changeover.")
    planned_on = fields.Datetime(
        string="Planned Restart", required=True,
        default=fields.Datetime.now, tracking=True)
    released_on = fields.Datetime(
        string="Released On", readonly=True, copy=False, tracking=True)
    responsible_id = fields.Many2one(
        "res.users", string="Responsible", required=True,
        default=lambda self: self.env.user, tracking=True)
    state = fields.Selection(
        [("draft", "Draft"), ("in_progress", "In Progress"),
         ("ready", "Ready"), ("released", "Released")],
        default="draft", required=True, tracking=True, index=True,
        copy=False)
    item_ids = fields.One2many(
        "clc.item", "check_id", string="Clearance Items")
    item_count = fields.Integer(
        string="Items", compute="_compute_counts", store=True)
    done_item_count = fields.Integer(
        string="Done Items", compute="_compute_counts", store=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True,
        default=lambda self: self.env.company)
    note = fields.Text()

    @api.depends("item_ids", "item_ids.state")
    def _compute_counts(self):
        for rec in self:
            rec.item_count = len(rec.item_ids)
            rec.done_item_count = len(
                rec.item_ids.filtered(lambda i: i.state == "done"))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "clc.check") or _("CLR-%s") % fields.Date.context_today(
                    self).strftime("%Y%m%d")
        return super().create(vals_list)

    @api.constrains("planned_on", "released_on")
    def _check_dates(self):
        for rec in self:
            if rec.released_on and rec.planned_on \
                    and rec.released_on < rec.planned_on:
                raise ValidationError(_(
                    "Clearance %s cannot be released before it was planned.",
                    rec.name))

    def action_start(self):
        for rec in self:
            if rec.state != "draft":
                raise ValidationError(_(
                    "Only a draft clearance can be started."))
            rec.state = "in_progress"
        return True

    def action_mark_ready(self):
        for rec in self:
            if rec.state != "in_progress":
                raise ValidationError(_(
                    "Only an in-progress clearance can be marked ready."))
            if rec.item_count == 0:
                raise ValidationError(_(
                    "Clearance %s needs at least one checklist item.", rec.name))
            if rec.done_item_count != rec.item_count:
                raise ValidationError(_(
                    "Clearance %s still has incomplete checklist items.",
                    rec.name))
            rec.state = "ready"
        return True

    def action_release(self):
        for rec in self:
            if rec.state != "ready":
                raise ValidationError(_(
                    "Only a ready clearance can be released."))
            rec.write({
                "state": "released",
                "released_on": fields.Datetime.now(),
            })
            rec.message_post(body=_("Line clearance released."))
        return True
