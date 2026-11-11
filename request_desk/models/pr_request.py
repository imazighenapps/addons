# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class PrRequest(models.Model):
    _name = "pr.request"
    _description = "Purchase Request"
    _inherit = ["mail.thread"]
    _order = "needed_on, id desc"

    name = fields.Char(
        required=True, tracking=True, copy=False,
        default=lambda self: _("New Request"))
    requester_id = fields.Many2one(
        "res.users", string="Requester", required=True,
        default=lambda self: self.env.user, tracking=True, index=True)
    needed_on = fields.Date(
        string="Needed On", required=True,
        default=fields.Date.context_today, tracking=True)
    state = fields.Selection(
        [("draft", "Draft"), ("submitted", "Submitted"),
         ("approved", "Approved"), ("ordered", "Ordered"),
         ("done", "Done"), ("cancel", "Cancelled")],
        default="draft", required=True, tracking=True, index=True,
        copy=False)
    line_ids = fields.One2many(
        "pr.request.line", "request_id", string="Request Lines", copy=True)
    line_count = fields.Integer(
        string="Lines", compute="_compute_totals", store=True)
    total_qty = fields.Float(
        string="Total Quantity", compute="_compute_totals", store=True,
        digits="Product Unit of Measure")
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)
    note = fields.Text(string="Internal Note")
    active = fields.Boolean(default=True)

    @api.depends("line_ids", "line_ids.quantity")
    def _compute_totals(self):
        for request in self:
            request.line_count = len(request.line_ids)
            request.total_qty = sum(request.line_ids.mapped("quantity"))

    @api.constrains("line_ids")
    def _check_lines(self):
        for request in self:
            if request.state in ("approved", "ordered", "done") and not request.line_ids:
                raise ValidationError(_(
                    "Approved request %s must keep at least one line.",
                    request.name))

    def action_submit(self):
        for request in self:
            if request.state != "draft":
                raise UserError(_("Only draft requests can be submitted."))
            if not request.line_ids:
                raise UserError(_(
                    "Add at least one request line before submitting %s.",
                    request.name))
            request.state = "submitted"
            request.message_post(body=_("The request was submitted for approval."))
        return True

    def action_approve(self):
        for request in self:
            if request.state != "submitted":
                raise UserError(_("Only submitted requests can be approved."))
            request.state = "approved"
            request.message_post(body=_("The request was approved."))
        return True

    def action_mark_ordered(self):
        for request in self:
            if request.state != "approved":
                raise UserError(_("Only approved requests can be marked as ordered."))
            request.state = "ordered"
            request.message_post(body=_("The request was marked as ordered."))
        return True

    def action_done(self):
        for request in self:
            if request.state != "ordered":
                raise UserError(_("Only ordered requests can be closed."))
            request.state = "done"
            request.message_post(body=_("The request was completed."))
        return True

    def action_cancel(self):
        for request in self:
            if request.state in ("ordered", "done"):
                raise UserError(_("Ordered or completed requests cannot be cancelled."))
            request.state = "cancel"
            request.message_post(body=_("The request was cancelled."))
        return True

    def action_reset_draft(self):
        for request in self:
            if request.state not in ("submitted", "cancel"):
                raise UserError(_("Only submitted or cancelled requests can be reset."))
            request.state = "draft"
            request.message_post(body=_("The request was reset to draft."))
        return True
