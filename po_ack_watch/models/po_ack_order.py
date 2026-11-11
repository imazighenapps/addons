# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class PoAckOrder(models.Model):
    _name = "po.ack.order"
    _description = "Purchase Order Acknowledgement"
    _inherit = ["mail.thread"]
    _order = "deadline_date asc, id desc"

    name = fields.Char(string="PO Reference", required=True, tracking=True)
    partner_id = fields.Many2one(
        "res.partner", string="Supplier", required=True, tracking=True,
        index=True)
    sent_date = fields.Date(
        string="Sent On", required=True, default=fields.Date.context_today,
        tracking=True)
    deadline_date = fields.Date(
        string="Ack Deadline", required=True, tracking=True,
        help="Date by which the supplier should acknowledge the order.")
    acknowledged_on = fields.Date(
        string="Acknowledged On", readonly=True, copy=False, tracking=True)
    acknowledged_by = fields.Char(
        string="Acknowledged By",
        help="Supplier contact or reference who confirmed the order.")
    followup_ids = fields.One2many(
        "po.ack.followup", "ack_id", string="Follow-ups")
    followup_count = fields.Integer(
        string="Follow-ups", compute="_compute_followups", store=True)
    days_waiting = fields.Integer(
        string="Days Waiting", compute="_compute_waiting", store=True,
        help="Days since the order was sent while it remains unacknowledged.")
    is_overdue = fields.Boolean(
        string="Overdue", compute="_compute_waiting", store=True, index=True,
        help="True when the deadline passed and the order is not acknowledged.")
    state = fields.Selection(
        [("waiting", "Waiting"), ("acknowledged", "Acknowledged")],
        default="waiting", required=True, tracking=True, index=True)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)
    active = fields.Boolean(default=True)
    note = fields.Text()

    @api.depends("followup_ids")
    def _compute_followups(self):
        for order in self:
            order.followup_count = len(order.followup_ids)

    @api.depends("sent_date", "deadline_date", "state")
    def _compute_waiting(self):
        today = fields.Date.context_today(self)
        for order in self:
            if order.state == "acknowledged":
                order.days_waiting = 0
                order.is_overdue = False
            else:
                base = order.sent_date or today
                order.days_waiting = max((today - base).days, 0)
                order.is_overdue = bool(
                    order.deadline_date and order.deadline_date < today)

    @api.constrains("sent_date", "deadline_date")
    def _check_dates(self):
        for order in self:
            if order.deadline_date and order.sent_date \
                    and order.deadline_date < order.sent_date:
                raise ValidationError(_(
                    "The acknowledgement deadline of %s cannot come before "
                    "the sent date.", order.name))

    def action_acknowledge(self):
        for order in self:
            if order.state != "waiting":
                raise ValidationError(_(
                    "The purchase order %s is already acknowledged.",
                    order.name))
            order.write({
                "state": "acknowledged",
                "acknowledged_on": fields.Date.context_today(order),
            })
            order.message_post(body=_(
                "The supplier acknowledgement has been recorded."))
        return True
