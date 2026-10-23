# -*- coding: utf-8 -*-
import hashlib
import secrets
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from .qes_provider import LEVELS


class QesParticipant(models.Model):
    _name = "qes.participant"
    _description = "QES Participant"

    envelope_id = fields.Many2one("qes.envelope", required=True, ondelete="cascade")
    partner_id = fields.Many2one("res.partner", string="Contact")
    name = fields.Char(required=True)
    email = fields.Char(required=True)
    phone = fields.Char()
    role = fields.Selection(
        [("signer", "Signer"), ("visa", "Visa"), ("cc", "Copy"), ("sealer", "Sealer")],
        default="signer",
        required=True,
    )
    sequence = fields.Integer(default=10)
    required_level = fields.Selection(LEVELS, default="ses", required=True)
    obtained_level = fields.Selection(LEVELS, readonly=True)
    auth_means = fields.Selection(
        [("email", "Email Link"), ("sms", "SMS OTP"), ("videoid", "Video ID"), ("eid", "eID")],
        default="email",
    )
    access_token = fields.Char(default=lambda self: secrets.token_hex(16), copy=False)
    sign_url = fields.Char(string="Signature URL", readonly=True)
    signed_on = fields.Datetime(readonly=True)
    cert_info = fields.Text(string="Certificate Info", readonly=True)

    def action_demo_sign(self):
        for part in self:
            env = part.envelope_id
            if env.account_id.provider_id.code != "demo":
                raise UserError(_("Demo signing is only available on the demo provider."))
            if part.signed_on:
                raise UserError(_("Already signed."))
            part.write({
                "signed_on": fields.Datetime.now(),
                "obtained_level": part.required_level,
                "cert_info": "DEMO-QC serial DEMO-%s (non-qualified, test only)" % part.id,
            })
            env._log("signed", "Participant %s signed at level %s." % (part.email, part.required_level),
                     actor=part.email)
            remaining = env.participant_ids.filtered(lambda p: p.role == "signer" and not p.signed_on)
            env.state = "signed" if not remaining else "partial"
            if env.state == "signed":
                env._demo_finalize()


class QesField(models.Model):
    _name = "qes.field"
    _description = "QES Signature Field Placement"

    document_id = fields.Many2one("qes.document", required=True, ondelete="cascade")
    participant_id = fields.Many2one("qes.participant", required=True, ondelete="cascade")
    ftype = fields.Selection(
        [("signature", "Signature"), ("visa", "Visa"), ("text", "Text"), ("checkbox", "Checkbox")],
        default="signature",
        required=True,
    )
    page = fields.Integer(default=1)
    pos_x = fields.Integer(string="X")
    pos_y = fields.Integer(string="Y")
    anchor = fields.Char(help="e.g. anchor=client signature")
    mandatory = fields.Boolean(default=True)
