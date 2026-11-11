# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class OtdCommitment(models.Model):
    _name = "otd.commitment"
    _description = "Delivery Commitment"
    _inherit = ["mail.thread"]
    _order = "promised_on, id desc"

    name = fields.Char(
        required=True,
        default=lambda self: _("Ship %s")
        % fields.Date.context_today(self),
        help="Reference of the commitment, generated at creation.")
    order_ref = fields.Char(
        required=True, tracking=True,
        help="Reference of the order whose promise is watched.")
    customer_name = fields.Char(
        string="Customer", required=True, tracking=True)
    promised_on = fields.Date(
        string="Promised On", required=True, tracking=True,
        help="Delivery date promised to the customer.")
    shipped_on = fields.Date(
        string="Shipped On", readonly=True, copy=False,
        help="Date the goods really left the warehouse.")
    delay_days = fields.Integer(
        string="Delay (days)", compute="_compute_otd", store=True,
        help="Days between the promise and the real shipment. "
             "Negative for an early delivery.")
    on_time = fields.Boolean(
        string="On Time", compute="_compute_otd", store=True,
        help="True when the goods left at the promised date or "
             "before it.")
    state = fields.Selection(
        [("open", "Awaiting Shipment"), ("shipped", "Shipped")],
        default="open", required=True, copy=False, tracking=True,
        index=True)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)
    note = fields.Text()

    @api.depends("promised_on", "shipped_on")
    def _compute_otd(self):
        for commitment in self:
            if commitment.shipped_on and commitment.promised_on:
                delay = (commitment.shipped_on
                         - commitment.promised_on).days
                commitment.delay_days = delay
                commitment.on_time = delay <= 0
            else:
                commitment.delay_days = 0
                commitment.on_time = False

    @api.constrains("state", "shipped_on")
    def _check_shipment(self):
        for commitment in self:
            if commitment.state == "shipped" and not commitment.shipped_on:
                raise ValidationError(_(
                    "The commitment for %s must carry the date its goods "
                    "shipped.", commitment.order_ref))

    def action_ship_today(self):
        for commitment in self:
            if commitment.state != "open":
                raise UserError(_(
                    "The goods of %s already shipped.",
                    commitment.order_ref))
            commitment.write({
                "state": "shipped",
                "shipped_on": fields.Date.context_today(commitment),
            })
            commitment.message_post(body=_(
                "The goods shipped; the promise is scored."))
        return True

    def action_back_to_open(self):
        for commitment in self:
            if commitment.state != "shipped":
                raise UserError(_(
                    "The goods of %s did not ship yet.",
                    commitment.order_ref))
            commitment.write({
                "state": "open", "shipped_on": False,
            })
            commitment.message_post(body=_(
                "The commitment was reopened."))
        return True
