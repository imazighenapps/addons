# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from .qr_tools import (
    make_rf_reference, is_rf_reference, make_qrr_reference, is_qrr_reference,
    is_qr_iban, build_epc_payload,
)


class QrpayConfig(models.Model):
    _name = "qrpay.config"
    _description = "QR Pay Pro Configuration"

    name = fields.Char(default="Default", required=True)
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True)
    rf_prefix = fields.Char(string="RF Base Prefix", default="INV")
    rf_sequence_id = fields.Many2one("ir.sequence", string="RF Sequence")
    qrr_sequence_id = fields.Many2one("ir.sequence", string="QRR Sequence")
    default_purpose = fields.Char(string="Default EPC Purpose (e.g. SUPP)")
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ("company_unique", "UNIQUE(company_id)", "One QR Pay configuration per company."),
    ]


class AccountMove(models.Model):
    _inherit = "account.move"

    qr_pay_reference = fields.Char(
        string="QR Reference", copy=False,
        help="Stored RF/SCOR/QRR reference used for payment QR.")
    qr_pay_reference_type = fields.Selection(
        [("none", "None"), ("rf", "RF (ISO 11649)"), ("scor", "SCOR"),
         ("qrr", "QRR (Swiss)"), ("non", "NON")],
        string="QR Reference Type", default="none",
    )
    qr_pay_purpose = fields.Char(string="EPC Purpose")
    qr_pay_valid = fields.Boolean(string="QR Valid", compute="_compute_qr_pay", store=True)
    qr_pay_error = fields.Char(string="QR Issue", compute="_compute_qr_pay", store=True)

    _sql_constraints = [
        ("qr_ref_unique", "UNIQUE(company_id, qr_pay_reference)", "QR reference must be unique per company."),
    ]

    @api.depends("qr_pay_reference", "qr_pay_reference_type", "partner_bank_id",
                 "currency_id", "amount_total")
    def _compute_qr_pay(self):
        for move in self:
            ok, msg = move._qr_pay_check()
            move.qr_pay_valid = ok
            move.qr_pay_error = "" if ok else msg

    def _qr_pay_check(self):
        self.ensure_one()
        if self.qr_pay_reference_type in (False, "none") or not self.qr_pay_reference:
            return True, ""
        ref = self.qr_pay_reference
        rtype = self.qr_pay_reference_type
        if rtype in ("rf", "scor") and not is_rf_reference(ref):
            return False, _("Invalid RF/SCOR reference (ISO 11649).")
        if rtype == "qrr" and not is_qrr_reference(ref):
            return False, _("Invalid QRR reference (27 digits, mod10r).")
        return True, ""

    def action_qr_pay_assign_rf(self):
        for move in self:
            config = self.env["qrpay.config"].search(
                [("company_id", "=", move.company_id.id)], limit=1)
            prefix = config.rf_prefix if config else "INV"
            seq_code = config.rf_sequence_id.code if config and config.rf_sequence_id else "qrpay.rf"
            base = "%s%s" % (prefix, self.env["ir.sequence"].next_by_code(seq_code) or move.name or move.id)
            ref = make_rf_reference(base)
            if not ref:
                raise UserError(_("Could not build an RF reference from '%s'.") % base)
            move.write({"qr_pay_reference": ref, "qr_pay_reference_type": "rf"})

    def action_qr_pay_assign_qrr(self):
        for move in self:
            config = self.env["qrpay.config"].search(
                [("company_id", "=", move.company_id.id)], limit=1)
            seq_code = config.qrr_sequence_id.code if config and config.qrr_sequence_id else "qrpay.qrr"
            base = self.env["ir.sequence"].next_by_code(seq_code) or str(move.id or 0)
            ref = make_qrr_reference(base)
            move.write({"qr_pay_reference": ref, "qr_pay_reference_type": "qrr"})

    def action_qr_pay_preview_epc(self):
        self.ensure_one()
        bank = self.partner_bank_id or self.company_id.partner_id.bank_ids[:1]
        ok, payload = build_epc_payload(
            name=self.company_id.name,
            iban=bank.acc_number if bank else "",
            amount=self.amount_total if self.is_invoice() else 0.0,
            currency=self.currency_id.name,
            bic=getattr(bank, "bank_bic", "") or "",
            purpose=self.qr_pay_purpose or "",
            rf_reference=self.qr_pay_reference if self.qr_pay_reference_type in ("rf", "scor") else "",
            remittance="" if self.qr_pay_reference_type in ("rf", "scor") else (self.payment_reference or self.name or ""),
        )
        if not ok:
            raise UserError(payload)
        return {
            "type": "ir.actions.act_window",
            "name": _("EPC Payload Preview"),
            "res_model": "qrpay.payload.preview",
            "view_mode": "form",
            "target": "new",
            "context": {"default_payload": payload},
        }


class QrpayPayloadPreview(models.TransientModel):
    _name = "qrpay.payload.preview"
    _description = "EPC Payload Preview"

    payload = fields.Text(readonly=True)
