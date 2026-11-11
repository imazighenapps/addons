# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class LabSample(models.Model):
    _name = "lab.sample"
    _description = "Lab Sample Request"
    _inherit = ["mail.thread"]
    _order = "sent_on desc, id desc"

    name = fields.Char(
        required=True,
        default=lambda self: _("LAB %s")
        % fields.Date.context_today(self),
        help="Reference of the sample request, generated at creation.")
    lot_ref = fields.Char(
        string="Lot Reference", required=True, tracking=True,
        help="Lot or batch the sample belongs to.")
    barcode = fields.Char(
        string="Barcode", tracking=True,
        help="Barcode printed on the sample request.")
    laboratory = fields.Char(
        string="External Lab", required=True, tracking=True,
        help="External laboratory receiving the sample.")
    sent_on = fields.Date(
        string="Sent On", required=True,
        default=fields.Date.context_today, tracking=True)
    received_on = fields.Date(
        string="Received On", readonly=True, copy=False, tracking=True)
    outcome = fields.Selection(
        [("pending", "Pending"), ("pass", "Pass"), ("fail", "Fail")],
        default="pending", required=True, tracking=True,
        help="Outcome of the analysis once the result is received.")
    result_note = fields.Text(
        string="Result",
        help="Result details returned by the laboratory.")
    state = fields.Selection(
        [("sent", "Sent"), ("received", "Result Received")],
        default="sent", required=True, copy=False, tracking=True,
        index=True)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company", required=True,
        default=lambda self: self.env.company, index=True)
    note = fields.Text()

    @api.constrains("sent_on", "received_on")
    def _check_dates(self):
        for record in self:
            if record.received_on and record.received_on < record.sent_on:
                raise ValidationError(_(
                    "The received date of %s cannot come before the sent "
                    "date.", record.name))

    @api.constrains("outcome", "state")
    def _check_outcome(self):
        for record in self:
            if record.state == "received" and record.outcome == "pending":
                raise ValidationError(_(
                    "The sample %s must have a pass or fail outcome before "
                    "the result can be received.", record.name))

    def action_receive(self):
        for record in self:
            if record.state != "sent":
                raise ValidationError(_(
                    "The result for sample %s is already received.",
                    record.name))
            if record.outcome == "pending":
                raise ValidationError(_(
                    "Set a pass or fail outcome for %s before receiving "
                    "the result.", record.name))
            record.write({
                "state": "received",
                "received_on": fields.Date.context_today(record),
            })
            record.message_post(body=_(
                "The laboratory result was received."))
        return True
