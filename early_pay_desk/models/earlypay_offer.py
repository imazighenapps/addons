# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class EarlypayOffer(models.Model):
    _name = "earlypay.offer"
    _description = "Early Payment Offer"
    _inherit = ["mail.thread"]
    _order = "discount_deadline, id"

    name = fields.Char(
        string="Reference", required=True, tracking=True,
        help="Vendor bill or internal reference of the offer.")
    partner_id = fields.Many2one(
        "res.partner", string="Vendor", required=True, tracking=True)
    currency_id = fields.Many2one(
        "res.currency", required=True,
        default=lambda self: self.env.company.currency_id)
    gross_amount = fields.Monetary(
        required=True, currency_field="currency_id", tracking=True,
        help="Invoice amount before the early payment discount.")
    discount_rate = fields.Float(
        string="Discount Rate (%)", required=True, tracking=True,
        help="Percentage offered when paid before the discount deadline.")
    discount_amount = fields.Monetary(
        compute="_compute_amounts", store=True, currency_field="currency_id",
        help="Amount saved when the discount is captured.")
    net_amount = fields.Monetary(
        string="Net to Pay", compute="_compute_amounts", store=True,
        currency_field="currency_id",
        help="Amount to pay when the discount is captured.")
    invoice_date = fields.Date(default=fields.Date.context_today)
    discount_deadline = fields.Date(required=True, tracking=True)
    due_date = fields.Date(required=True, tracking=True)
    state = fields.Selection(
        [("open", "Open"), ("captured", "Captured"), ("missed", "Missed")],
        default="open", required=True, copy=False, tracking=True, index=True)
    decided_on = fields.Date(string="Decided On", readonly=True, copy=False)
    is_open = fields.Boolean(
        string="Still Open", compute="_compute_is_open", store=True,
        help="True while the offer is still open.")
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)
    note = fields.Text()

    @api.depends("gross_amount", "discount_rate")
    def _compute_amounts(self):
        for offer in self:
            discount = offer.gross_amount * (offer.discount_rate or 0.0) / 100.0
            offer.discount_amount = discount
            offer.net_amount = offer.gross_amount - discount

    @api.depends("state")
    def _compute_is_open(self):
        for offer in self:
            offer.is_open = offer.state == "open"

    @api.constrains("gross_amount", "discount_rate")
    def _check_values(self):
        for offer in self:
            if offer.gross_amount <= 0:
                raise ValidationError(_(
                    "The gross amount of %s must be above zero.", offer.name))
            if offer.discount_rate <= 0 or offer.discount_rate >= 100:
                raise ValidationError(_(
                    "The discount rate of %s must be between 0 and 100.",
                    offer.name))

    @api.constrains("invoice_date", "discount_deadline", "due_date")
    def _check_dates(self):
        for offer in self:
            if offer.invoice_date and offer.discount_deadline < offer.invoice_date:
                raise ValidationError(_(
                    "The discount deadline of %s cannot be before the invoice "
                    "date.", offer.name))
            if offer.due_date < offer.discount_deadline:
                raise ValidationError(_(
                    "The due date of %s cannot be before the discount deadline.",
                    offer.name))

    def action_capture(self):
        for offer in self:
            if offer.state != "open":
                raise UserError(_("Only an open offer can be captured."))
            offer.write({
                "state": "captured",
                "decided_on": fields.Date.context_today(offer),
            })
            offer.message_post(body=_(
                "Discount captured: %s saved.", offer.discount_amount))
        return True

    def action_miss(self):
        for offer in self:
            if offer.state != "open":
                raise UserError(_("Only an open offer can be marked as missed."))
            offer.write({
                "state": "missed",
                "decided_on": fields.Date.context_today(offer),
            })
            offer.message_post(body=_(
                "Discount missed on %s.", offer.name))
        return True

    def action_reopen(self):
        for offer in self:
            if offer.state == "open":
                raise UserError(_("This offer is already open."))
            offer.write({"state": "open", "decided_on": False})
            offer.message_post(body=_("Offer reopened."))
        return True
