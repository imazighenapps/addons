# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class LotRecall(models.Model):
    _name = "lot.recall"
    _description = "Lot Recall"
    _inherit = ["mail.thread"]
    _order = "start_date desc, id desc"

    name = fields.Char(required=True, tracking=True, copy=False)
    product_name = fields.Char(
        string="Product", required=True, tracking=True,
        help="Product affected by the recall.")
    reason = fields.Text(required=True, tracking=True)
    start_date = fields.Date(
        required=True, default=fields.Date.context_today, tracking=True)
    state = fields.Selection(
        [("draft", "Draft"), ("active", "Active"),
         ("notifying", "Notifying"), ("closed", "Closed"),
         ("cancel", "Cancelled")],
        default="draft", required=True, tracking=True, index=True, copy=False)
    line_ids = fields.One2many(
        "lot.recall.line", "recall_id", string="Impacted Lines", copy=True)
    impact_count = fields.Integer(
        string="Impacted Lines", compute="_compute_totals", store=True)
    notified_count = fields.Integer(
        string="Notified", compute="_compute_totals", store=True)
    pending_count = fields.Integer(
        string="Pending", compute="_compute_totals", store=True)
    responsible_id = fields.Many2one(
        "res.users", string="Responsible", default=lambda self: self.env.user,
        tracking=True)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)
    note = fields.Text()
    active = fields.Boolean(default=True)

    @api.depends("line_ids", "line_ids.notified")
    def _compute_totals(self):
        for recall in self:
            recall.impact_count = len(recall.line_ids)
            recall.notified_count = len(recall.line_ids.filtered("notified"))
            recall.pending_count = recall.impact_count - recall.notified_count

    @api.constrains("line_ids", "state")
    def _check_active_has_lines(self):
        for recall in self:
            if recall.state in ("active", "notifying", "closed") and not recall.line_ids:
                raise ValidationError(_(
                    "Recall %s must have at least one impacted line.",
                    recall.name))

    def action_activate(self):
        for recall in self:
            if recall.state != "draft":
                raise UserError(_("Only draft recalls can be activated."))
            if not recall.line_ids:
                raise UserError(_(
                    "Add at least one impacted line before activating %s.",
                    recall.name))
            recall.state = "active"
            recall.message_post(body=_("The recall was activated."))
        return True

    def action_start_notifying(self):
        for recall in self:
            if recall.state != "active":
                raise UserError(_("Only active recalls can start notifications."))
            recall.state = "notifying"
            recall.message_post(body=_("Customer notifications have started."))
        return True

    def action_mark_all_notified(self):
        for recall in self:
            if recall.state != "notifying":
                raise UserError(_("Only recalls in notifying state can be marked notified."))
            pending = recall.line_ids.filtered(lambda line: not line.notified)
            pending.write({
                "notified": True,
                "notified_on": fields.Date.context_today(recall),
            })
            recall.message_post(body=_("All impacted customers were marked as notified."))
        return True

    def action_close(self):
        for recall in self:
            if recall.state != "notifying":
                raise UserError(_("Only recalls in notifying state can be closed."))
            if recall.pending_count:
                raise UserError(_(
                    "All impacted customers must be notified before closing %s.",
                    recall.name))
            recall.state = "closed"
            recall.message_post(body=_("The recall was closed."))
        return True

    def action_cancel(self):
        for recall in self:
            if recall.state == "closed":
                raise UserError(_("Closed recalls cannot be cancelled."))
            recall.state = "cancel"
            recall.message_post(body=_("The recall was cancelled."))
        return True
