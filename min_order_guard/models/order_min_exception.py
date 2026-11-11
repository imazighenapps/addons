# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class OrderMinException(models.Model):
    _name = "order.min.exception"
    _description = "Order Below Minimum"
    _inherit = ["mail.thread"]
    _order = "reference, id desc"

    name = fields.Char(
        required=True,
        default=lambda self: _("Exception %s")
        % fields.Date.context_today(self),
        help="Reference of the exception, generated at creation.")
    rule_id = fields.Many2one(
        "order.min.rule", string="Rule", required=True, index=True,
        tracking=True, help="Minimum the order collided with.")
    reference = fields.Char(
        required=True, tracking=True,
        help="Reference of the order that came in below the minimum.")
    order_amount = fields.Float(
        string="Order Amount", required=True,
        help="Value of the order when it arrived.")
    order_quantity = fields.Integer(
        string="Order Quantity", required=True,
        help="Quantity of the order when it arrived.")
    shortfall = fields.Float(
        string="Shortfall", compute="_compute_shortfall", store=True,
        help="Amount missing to reach the minimum.")
    reason = fields.Text(
        tracking=True,
        help="Written reason required when an exception is allowed.")
    state = fields.Selection(
        [("pending", "Pending"), ("allowed", "Allowed"),
         ("refused", "Refused")],
        default="pending", required=True, copy=False, tracking=True,
        index=True)
    decided_by = fields.Many2one(
        "res.users", string="Decided By", readonly=True, copy=False)
    decided_on = fields.Date(
        string="Decided On", readonly=True, copy=False)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)
    note = fields.Text()

    @api.depends("rule_id", "rule_id.min_amount", "order_amount")
    def _compute_shortfall(self):
        for exception in self:
            minimum = max(exception.rule_id.min_amount, 0.0)
            exception.shortfall = max(
                minimum - (exception.order_amount or 0.0), 0.0)

    @api.constrains("order_amount", "order_quantity")
    def _check_order_values(self):
        for exception in self:
            if exception.order_amount < 0.0 \
                    or exception.order_quantity < 0:
                raise ValidationError(_(
                    "The order values of %s must be positive.",
                    exception.reference))

    @api.constrains("state", "reason")
    def _check_reason(self):
        for exception in self:
            if exception.state == "allowed" and not exception.reason:
                raise ValidationError(_(
                    "Allowing %s below the minimum requires a written "
                    "reason.", exception.reference))

    def action_allow(self):
        for exception in self:
            if exception.state != "pending":
                raise UserError(_(
                    "The exception on %s is already decided.",
                    exception.reference))
            exception.write({
                "state": "allowed",
                "decided_by": self.env.user.id,
                "decided_on": fields.Date.context_today(exception),
            })
            exception.message_post(body=_(
                "The order was allowed below the minimum: %s.",
                exception.reason or _("no reason written")))
        return True

    def action_refuse(self):
        for exception in self:
            if exception.state != "pending":
                raise UserError(_(
                    "The exception on %s is already decided.",
                    exception.reference))
            exception.write({
                "state": "refused",
                "decided_by": self.env.user.id,
                "decided_on": fields.Date.context_today(exception),
            })
            exception.message_post(body=_(
                "The order below the minimum was refused."))
        return True
