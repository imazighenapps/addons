# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class RmaRequest(models.Model):
    _name = "rma.request"
    _description = "Return Request"
    _inherit = ["mail.thread"]
    _order = "requested_on desc, id desc"

    name = fields.Char(
        required=True, tracking=True,
        default=lambda self: _("RMA %s") % fields.Date.context_today(self))
    customer_name = fields.Char(
        string="Customer", required=True, tracking=True)
    requested_on = fields.Date(
        string="Requested On", required=True, default=fields.Date.context_today,
        tracking=True)
    reason = fields.Text(required=True, tracking=True)
    state = fields.Selection(
        [("draft", "Draft"), ("approved", "Approved"),
         ("received", "Received"), ("resolved", "Resolved"),
         ("refused", "Refused")],
        default="draft", required=True, tracking=True, index=True)
    resolution = fields.Selection(
        [("keep", "Keep"), ("scrap", "Scrap"), ("credit", "Credit")],
        tracking=True)
    credit_amount = fields.Monetary(
        string="Credit Amount", currency_field="currency_id", default=0.0)
    line_ids = fields.One2many(
        "rma.line", "request_id", string="Return Lines", copy=True)
    line_count = fields.Integer(
        string="Lines", compute="_compute_totals", store=True)
    total_qty = fields.Float(
        string="Returned Qty", compute="_compute_totals", store=True)
    total_value = fields.Monetary(
        string="Returned Value", compute="_compute_totals",
        store=True, currency_field="currency_id")
    currency_id = fields.Many2one(
        "res.currency", required=True,
        default=lambda self: self.env.company.currency_id)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)
    note = fields.Text()

    @api.depends("line_ids", "line_ids.quantity", "line_ids.subtotal")
    def _compute_totals(self):
        for request in self:
            request.line_count = len(request.line_ids)
            request.total_qty = sum(request.line_ids.mapped("quantity"))
            request.total_value = sum(request.line_ids.mapped("subtotal"))

    @api.constrains("state", "credit_amount")
    def _check_credit_amount(self):
        for request in self:
            if request.credit_amount < 0:
                raise ValidationError(_(
                    "The credit amount of %s cannot be negative.",
                    request.name))

    def action_approve(self):
        for request in self:
            if request.state != "draft":
                raise UserError(_("Only draft returns can be approved."))
            if not request.line_ids:
                raise UserError(_(
                    "Return %s must contain at least one line before "
                    "approval.", request.name))
            request.state = "approved"
            request.message_post(body=_("The return request was approved."))
        return True

    def action_refuse(self):
        for request in self:
            if request.state not in ("draft", "approved"):
                raise UserError(_(
                    "Only draft or approved returns can be refused."))
            request.state = "refused"
            request.message_post(body=_("The return request was refused."))
        return True

    def action_receive(self):
        for request in self:
            if request.state != "approved":
                raise UserError(_("Only approved returns can be received."))
            request.state = "received"
            request.message_post(body=_("The return was received."))
        return True

    def action_resolve(self):
        for request in self:
            if request.state != "received":
                raise UserError(_("Only received returns can be resolved."))
            if not request.resolution:
                raise UserError(_(
                    "Choose a resolution before resolving %s.", request.name))
            request.state = "resolved"
            request.message_post(body=_(
                "The return was resolved as %s.", request.resolution))
        return True
