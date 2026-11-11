# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class AuditBinder(models.Model):
    _name = "audit.binder"
    _description = "Audit Binder"
    _inherit = ["mail.thread"]
    _order = "period_start desc, id desc"

    name = fields.Char(required=True, tracking=True)
    period_start = fields.Date(required=True, tracking=True)
    period_end = fields.Date(required=True, tracking=True)
    item_ids = fields.One2many("audit.binder.item", "binder_id",
                               string="Evidence Items")
    item_count = fields.Integer(
        string="Items", compute="_compute_progress", store=True)
    missing_item_count = fields.Integer(
        string="Missing Items", compute="_compute_progress", store=True)
    state = fields.Selection(
        [("draft", "Draft"), ("collecting", "Collecting"),
         ("closed", "Closed")],
        default="draft", required=True, copy=False, tracking=True, index=True)
    closed_on = fields.Date(string="Closed On", readonly=True, copy=False)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)
    note = fields.Text()

    @api.depends("item_ids", "item_ids.ready")
    def _compute_progress(self):
        for binder in self:
            items = binder.item_ids
            binder.item_count = len(items)
            binder.missing_item_count = len(items.filtered(
                lambda item: not item.ready))

    @api.constrains("period_start", "period_end")
    def _check_period(self):
        for binder in self:
            if binder.period_end < binder.period_start:
                raise ValidationError(_(
                    "The period end of %s cannot be before its start.",
                    binder.name))

    def action_start_collecting(self):
        for binder in self:
            if binder.state != "draft":
                raise ValidationError(_(
                    "Only a draft binder can start collecting evidence."))
            if not binder.item_ids:
                raise ValidationError(_(
                    "Add at least one evidence item before collecting %s.",
                    binder.name))
            binder.state = "collecting"
            binder.message_post(body=_(
                "The audit binder started collecting evidence."))
        return True

    def action_close(self):
        for binder in self:
            if binder.state != "collecting":
                raise ValidationError(_(
                    "Only a binder in collection can be closed."))
            if binder.missing_item_count:
                raise ValidationError(_(
                    "Mark every evidence item as ready before closing %s.",
                    binder.name))
            binder.write({
                "state": "closed",
                "closed_on": fields.Date.context_today(binder),
            })
            binder.message_post(body=_(
                "The audit binder was closed with all evidence ready."))
        return True
