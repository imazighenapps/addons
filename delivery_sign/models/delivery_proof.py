# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class DeliveryProof(models.Model):
    _name = "delivery.proof"
    _description = "Delivery Proof"
    _inherit = ["mail.thread"]
    _order = "delivery_date desc, id desc"

    name = fields.Char(
        required=True, tracking=True,
        help="Delivery reference or shipment number.")
    partner_id = fields.Many2one(
        "res.partner", string="Customer", required=True, tracking=True,
        help="Customer receiving the delivery.")
    responsible_id = fields.Many2one(
        "res.users", string="Driver", default=lambda self: self.env.user,
        tracking=True, help="Person responsible for the delivery.")
    delivery_date = fields.Date(
        string="Delivery Date", required=True,
        default=fields.Date.context_today, tracking=True)
    recipient_name = fields.Char(
        string="Recipient", help="Name of the person who received the goods.")
    signature_ok = fields.Boolean(
        string="Signature Captured", default=False, tracking=True,
        help="Indicates that a customer signature was collected.")
    photo_ok = fields.Boolean(
        string="Photo Captured", default=False, tracking=True,
        help="Indicates that a delivery photo was collected.")
    proof_complete = fields.Boolean(
        string="Proof Complete", compute="_compute_proof_complete", store=True,
        help="True when both signature and photo evidence are present.")
    state = fields.Selection(
        [("pending", "Pending"), ("signed", "Signed")],
        default="pending", required=True, tracking=True, index=True)
    signed_on = fields.Date(string="Signed On", readonly=True, copy=False)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)
    note = fields.Text()

    @api.depends("signature_ok", "photo_ok")
    def _compute_proof_complete(self):
        for proof in self:
            proof.proof_complete = bool(proof.signature_ok and proof.photo_ok)

    @api.constrains("delivery_date", "signed_on")
    def _check_dates(self):
        for proof in self:
            if proof.signed_on and proof.delivery_date \
                    and proof.signed_on < proof.delivery_date:
                raise ValidationError(_(
                    "The signature date of %s cannot be before the delivery "
                    "date.", proof.name))

    @api.constrains("state", "signature_ok", "recipient_name")
    def _check_signed_requirements(self):
        for proof in self:
            if proof.state == "signed":
                if not proof.signature_ok:
                    raise ValidationError(_(
                        "A signature is required before marking %s as signed.",
                        proof.name))
                if not proof.recipient_name:
                    raise ValidationError(_(
                        "A recipient name is required before marking %s as "
                        "signed.", proof.name))

    def action_mark_signed(self):
        for proof in self:
            if proof.state == "signed":
                raise ValidationError(_(
                    "The delivery proof %s is already signed.", proof.name))
            if not proof.signature_ok:
                raise ValidationError(_(
                    "Capture the customer signature before signing %s.",
                    proof.name))
            if not proof.recipient_name:
                raise ValidationError(_(
                    "Set the recipient name before signing %s.", proof.name))
            proof.write({
                "state": "signed",
                "signed_on": fields.Date.context_today(proof),
            })
            proof.message_post(body=_(
                "The delivery proof has been signed and recorded."))
        return True
