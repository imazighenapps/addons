# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class YousignConnection(models.Model):
    _name = "yousign.connection"
    _description = "Yousign Connection"
    _inherit = ["mail.thread"]

    name = fields.Char(required=True)
    company_id = fields.Many2one("res.company", required=True, default=lambda self: self.env.company)
    api_key_ref = fields.Char(string="API Key Reference")
    environment = fields.Selection([("sandbox", "Sandbox"), ("production", "Production")], default="sandbox", required=True)
    state = fields.Selection([("draft", "Draft"), ("active", "Active")], default="draft", tracking=True)
    active = fields.Boolean(default=True)

    def action_activate(self):
        for rec in self:
            if not rec.api_key_ref:
                raise UserError(_("Set the API key reference before activating."))
            rec.state = "active"
        return True


class YousignRequest(models.Model):
    _name = "yousign.request"
    _description = "Yousign Signature Request"
    _inherit = ["mail.thread"]
    _order = "create_date desc, id desc"

    name = fields.Char(required=True, copy=False, default="New")
    connection_id = fields.Many2one("yousign.connection", required=True, ondelete="restrict")
    company_id = fields.Many2one(related="connection_id.company_id", store=True)
    partner_id = fields.Many2one("res.partner", string="Customer")
    document_name = fields.Char(required=True, string="Document")
    external_id = fields.Char(string="Yousign ID", copy=False)
    signed_at = fields.Datetime()
    expires_on = fields.Date()
    proof_ref = fields.Char(string="Proof Reference")
    state = fields.Selection(
        [("draft", "Draft"), ("sent", "Sent"), ("signed", "Signed"),
         ("declined", "Declined"), ("expired", "Expired"), ("canceled", "Canceled")],
        default="draft", required=True, tracking=True)
    signer_ids = fields.One2many("yousign.signer", "request_id", string="Signers")
    event_ids = fields.One2many("yousign.event", "request_id")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("yousign.request") or "YS"
        return super().create(vals_list)

    @api.constrains("expires_on")
    def _check_expiry(self):
        for rec in self:
            if rec.expires_on and rec.signed_at and rec.expires_on < rec.signed_at.date():
                raise ValidationError(_("Expiry date cannot be before the signature date."))

    def _log(self, status, msg):
        self.env["yousign.event"].create({"request_id": self.id, "status": status, "message": msg})

    def action_send(self):
        for rec in self:
            if rec.state != "draft":
                raise UserError(_("Only draft requests can be sent."))
            if rec.connection_id.state != "active":
                raise UserError(_("Activate the Yousign connection first."))
            if not rec.signer_ids:
                raise UserError(_("Add at least one signer before sending."))
            rec.state = "sent"
            rec.external_id = rec.external_id or ("YS-%s" % rec.id)
            for signer in rec.signer_ids:
                signer.status = "pending"
            rec._log("sent", _("Signature request sent."))
        return True

    def action_mark_signed(self):
        for rec in self:
            if rec.state != "sent":
                raise UserError(_("Only sent requests can be marked signed."))
            rec.state = "signed"
            rec.signed_at = fields.Datetime.now()
            rec.proof_ref = rec.proof_ref or ("PROOF-%s" % rec.id)
            for signer in rec.signer_ids:
                signer.status = "signed"
            rec._log("signed", _("Document signed."))
        return True

    def action_mark_declined(self):
        for rec in self:
            if rec.state != "sent":
                raise UserError(_("Only sent requests can be declined."))
            rec.state = "declined"
            rec._log("declined", _("Signature declined."))
        return True

    def action_mark_expired(self):
        for rec in self:
            if rec.state != "sent":
                raise UserError(_("Only sent requests can expire."))
            rec.state = "expired"
            rec._log("expired", _("Request expired."))
        return True

    def action_cancel(self):
        for rec in self:
            if rec.state == "signed":
                raise UserError(_("Signed requests cannot be canceled."))
            rec.state = "canceled"
            rec._log("canceled", _("Request canceled."))
        return True


class YousignSigner(models.Model):
    _name = "yousign.signer"
    _description = "Yousign Signer"

    request_id = fields.Many2one("yousign.request", required=True, ondelete="cascade")
    partner_id = fields.Many2one("res.partner")
    name = fields.Char(required=True)
    email = fields.Char(required=True)
    status = fields.Selection(
        [("draft", "Draft"), ("pending", "Pending"), ("signed", "Signed"), ("declined", "Declined")],
        default="draft", required=True)

    @api.constrains("email")
    def _check_email(self):
        for rec in self:
            if "@" not in (rec.email or ""):
                raise ValidationError(_("Signer email must be valid."))


class YousignEvent(models.Model):
    _name = "yousign.event"
    _description = "Yousign Event"
    _order = "create_date desc, id desc"

    request_id = fields.Many2one("yousign.request", required=True, ondelete="cascade")
    status = fields.Char(required=True)
    message = fields.Text()
