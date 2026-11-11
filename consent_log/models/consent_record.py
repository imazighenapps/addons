# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class ConsentRecord(models.Model):
    _name = "consent.record"
    _description = "Consent Record"
    _inherit = ["mail.thread"]
    _order = "granted_on desc, id desc"

    name = fields.Char(
        string="Purpose", required=True, tracking=True,
        help="Purpose of the consent, for example newsletter or offers.")
    subject_id = fields.Many2one(
        "consent.subject", string="Contact", required=True,
        ondelete="cascade", index=True, tracking=True)
    channel = fields.Selection(
        [("email", "Email"), ("sms", "SMS"), ("phone", "Phone"),
         ("web", "Web Form"), ("paper", "Paper"), ("other", "Other")],
        default="email", required=True, tracking=True)
    source = fields.Char(
        required=True, tracking=True,
        help="Where the consent was collected, for example a form or event.")
    proof_ref = fields.Char(
        string="Proof Reference",
        help="Reference of the evidence kept for this consent.")
    granted_on = fields.Date(
        string="Granted On", required=True,
        default=fields.Date.context_today, tracking=True)
    expires_on = fields.Date(string="Expires On")
    withdrawn_on = fields.Date(string="Withdrawn On", readonly=True, copy=False)
    withdrawal_reason = fields.Text(string="Withdrawal Reason", readonly=True)
    state = fields.Selection(
        [("active", "Active"), ("withdrawn", "Withdrawn"),
         ("expired", "Expired")],
        default="active", required=True, tracking=True, index=True)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)
    note = fields.Text()

    @api.constrains("granted_on", "expires_on", "withdrawn_on")
    def _check_dates(self):
        for record in self:
            if record.expires_on and record.granted_on \
                    and record.expires_on < record.granted_on:
                raise ValidationError(_(
                    "The expiry date of consent \"%s\" cannot be before the "
                    "granted date.", record.name))
            if record.withdrawn_on and record.granted_on \
                    and record.withdrawn_on < record.granted_on:
                raise ValidationError(_(
                    "The withdrawal date of consent \"%s\" cannot be before "
                    "the granted date.", record.name))

    def action_withdraw(self):
        for record in self:
            if record.state == "withdrawn":
                raise UserError(_("This consent is already withdrawn."))
            reason = (record.withdrawal_reason or "").strip()
            if not reason:
                raise UserError(_(
                    "Enter a withdrawal reason before withdrawing the "
                    "consent \"%s\".", record.name))
            record.write({
                "state": "withdrawn",
                "withdrawn_on": fields.Date.context_today(record),
            })
            record.message_post(body=_(
                "The consent has been withdrawn. Reason: %s", reason))
        return True

    def action_expire(self):
        for record in self:
            if record.state != "active":
                raise UserError(_(
                    "Only an active consent can be marked as expired."))
            record.state = "expired"
            record.message_post(body=_("The consent has been marked as expired."))
        return True

    def action_reactivate(self):
        for record in self:
            if record.state != "expired":
                raise UserError(_(
                    "Only an expired consent can be reactivated."))
            record.state = "active"
            record.message_post(body=_("The consent has been reactivated."))
        return True
