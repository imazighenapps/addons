# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class RvdReturn(models.Model):
    _name = "rvd.return"
    _description = "Vendor Return Case"
    _inherit = ["mail.thread"]
    _order = "return_date desc, id desc"

    name = fields.Char(
        required=True, tracking=True,
        default=lambda self: _("Return %s") % fields.Date.context_today(self),
        help="Reference of the return case.")
    vendor_name = fields.Char(
        string="Supplier", required=True, tracking=True,
        help="Supplier receiving the rejected goods back.")
    reference = fields.Char(
        string="Vendor Reference",
        help="Supplier or claim reference tied to the return.")
    transport_ref = fields.Char(
        string="Transport Reference", tracking=True,
        help="Carrier or parcel reference used to trace the shipment.")
    return_date = fields.Date(
        string="Return Date", required=True,
        default=fields.Date.context_today, tracking=True)
    expected_credit = fields.Monetary(
        string="Expected Credit", currency_field="currency_id",
        tracking=True,
        help="Credit amount expected back from the supplier.")
    currency_id = fields.Many2one(
        "res.currency", required=True,
        default=lambda self: self.env.company.currency_id)
    credit_received = fields.Boolean(
        string="Credit Received", default=False, tracking=True,
        help="Ticked when the supplier credit note has been received.")
    state = fields.Selection(
        [("draft", "Draft"), ("sent", "Sent"),
         ("credited", "Credited"), ("closed", "Closed")],
        default="draft", required=True, copy=False, tracking=True,
        index=True)
    line_ids = fields.One2many(
        "rvd.return.line", "return_id", string="Return Lines")
    line_count = fields.Integer(
        string="Lines", compute="_compute_line_info", store=True)
    credit_pending = fields.Boolean(
        string="Credit Pending", compute="_compute_credit_pending",
        store=True,
        help="True while the return was sent and the credit is still awaited.")
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)
    note = fields.Text()

    @api.depends("line_ids")
    def _compute_line_info(self):
        for rec in self:
            rec.line_count = len(rec.line_ids)

    @api.depends("state", "credit_received", "expected_credit")
    def _compute_credit_pending(self):
        for rec in self:
            rec.credit_pending = bool(
                rec.state in ("sent", "credited")
                and not rec.credit_received
                and rec.expected_credit > 0)

    @api.constrains("expected_credit")
    def _check_expected_credit(self):
        for rec in self:
            if rec.expected_credit < 0:
                raise ValidationError(_(
                    "The expected credit of %s cannot be negative.",
                    rec.name))

    @api.constrains("credit_received", "expected_credit")
    def _check_credit_received_amount(self):
        for rec in self:
            if rec.credit_received and rec.expected_credit <= 0:
                raise ValidationError(_(
                    "A received credit on %s requires a positive expected "
                    "amount.", rec.name))

    def action_send(self):
        for rec in self:
            if rec.state != "draft":
                raise ValidationError(_(
                    "Only draft returns can be sent: %s.", rec.name))
            rec.state = "sent"
            rec.message_post(body=_("The return was sent to the supplier."))
        return True

    def action_mark_credited(self):
        for rec in self:
            if rec.state != "sent":
                raise ValidationError(_(
                    "Only sent returns can be marked credited: %s.",
                    rec.name))
            if rec.expected_credit <= 0:
                raise ValidationError(_(
                    "Set a positive expected credit before marking %s as "
                    "credited.", rec.name))
            rec.write({"state": "credited", "credit_received": True})
            rec.message_post(body=_("The supplier credit was received."))
        return True

    def action_close(self):
        for rec in self:
            if rec.state not in ("sent", "credited"):
                raise ValidationError(_(
                    "Only sent or credited returns can be closed: %s.",
                    rec.name))
            rec.state = "closed"
            rec.message_post(body=_("The return case was closed."))
        return True
