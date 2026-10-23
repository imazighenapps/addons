# -*- coding: utf-8 -*-
import base64
from xml.etree import ElementTree as ET
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from .qr_tools import decode_epc_payload


def _local(tag):
    return tag.rsplit("}", 1)[-1]


class CamtImport(models.TransientModel):
    _name = "qrpay.camt.import"
    _description = "Import camt.053 Bank Statement"

    data_file = fields.Binary(string="camt.053 File", required=True)
    filename = fields.Char()
    line_count = fields.Integer(readonly=True)
    note = fields.Text(readonly=True)

    def action_parse(self):
        self.ensure_one()
        try:
            root = ET.fromstring(base64.b64decode(self.data_file))
        except Exception as exc:
            raise UserError(_("Invalid XML file: %s") % exc)
        entries = []
        for stmt in root.iter():
            if _local(stmt.tag) == "Ntry":
                amt_el, iban_el, ref_el = None, None, None
                for el in stmt.iter():
                    local = _local(el.tag)
                    if local == "Amt":
                        amt_el = el
                    elif local == "IBAN" and iban_el is None:
                        iban_el = el
                    elif local in ("EndToEndId", "Ustrd", "CdtrRefInf"):
                        ref_el = el
                entries.append({
                    "amount": float((amt_el.text or "0").strip()) if amt_el is not None else 0.0,
                    "iban": (iban_el.text or "").strip() if iban_el is not None else "",
                    "ref": (ref_el.text or "").strip() if ref_el is not None else "",
                })
        self.write({
            "line_count": len(entries),
            "note": _("Parsed %d statement entries.") % len(entries),
        })
        return {
            "type": "ir.actions.act_window",
            "name": _("camt Import Result"),
            "res_model": "qrpay.camt.import",
            "res_id": self.id,
            "view_mode": "form",
            "target": "new",
        }

    def action_decode_qr_text(self, payload):
        """Decode an EPC/QR text payload into vendor-bill defaults."""
        decoded = decode_epc_payload(payload)
        if not decoded:
            raise UserError(_("Not a valid EPC QR payload."))
        return decoded
