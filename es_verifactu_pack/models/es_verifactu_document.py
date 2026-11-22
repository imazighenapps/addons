# -*- coding: utf-8 -*-
import base64
import hashlib
from datetime import date

from lxml import etree

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

STATES = [
    ("draft", "Brouillon"), ("ready", "Prête"), ("sent", "Envoyée"),
    ("accepted", "Acceptée"), ("rejected", "Refusée"),
]


class VerifactuDocument(models.Model):
    _name = "es.verifactu.document"
    _description = "Document VeriFactu"
    _inherit = ["mail.thread"]
    _order = "create_date desc, id desc"

    name = fields.Char(string="Référence", default="Nouveau", readonly=True, copy=False)
    company_id = fields.Many2one("res.company", required=True, default=lambda self: self.env.company)
    invoice_id = fields.Many2one(
        "account.move", string="Facture", required=True,
        domain="[('move_type','in',['out_invoice','out_refund']),('company_id','=',company_id),('state','=','posted')]")
    partner_id = fields.Many2one(related="invoice_id.partner_id", store=True)
    state = fields.Selection(STATES, default="draft", tracking=True)
    file_name = fields.Char(readonly=True)
    file_data = fields.Binary(string="Fichier", readonly=True)
    generated_at = fields.Datetime(readonly=True)
    external_id = fields.Char(string="Identifiant externe", tracking=True)
    status_note = fields.Text(string="Journal des statuts", readonly=True)

    previous_hash = fields.Char(string="Hash précédent", readonly=True)
    record_hash = fields.Char(string="Hash", readonly=True)
    qr_data = fields.Char(string="Données QR", readonly=True)

    _sql_constraints = [("es_verifactu_document_invoice_uniq", "unique(invoice_id)", "Document déjà existant pour cette facture.")]

    def action_generate(self):
        for rec in self:
            if not rec.name or rec.name == _("Nouveau"):
                rec.name = self.env["ir.sequence"].next_by_code("es.verifactu.document") or "VF"
            rec._generate()
            rec.state = "ready"
            rec._log(_("Registre VeriFactu généré."))

    def _generate(self):
        self.ensure_one()
        inv = self.invoice_id
        prev = self.search([("company_id", "=", self.company_id.id), ("id", "!=", self.id),
                            ("record_hash", "!=", False)], order="id desc", limit=1)
        prev_hash = prev.record_hash or "0" * 64
        payload = "|".join([
            self.company_id.vat or "", inv.name or "",
            (inv.invoice_date or date.today()).strftime("%d-%m-%Y"),
            "%.2f" % (inv.amount_total or 0.0), prev_hash,
        ])
        rhash = hashlib.sha256(payload.encode("utf-8")).hexdigest().upper()
        qr = "https://sede.agenciatributaria.gob.es/ValidarQR?nif=%s&num=%s&fecha=%s&importe=%.2f&huella=%s" % (
            (self.company_id.vat or ""), (inv.name or ""),
            (inv.invoice_date or date.today()).strftime("%d-%m-%Y"),
            (inv.amount_total or 0.0), rhash[:8])
        root = etree.Element("RegistroAlta")
        etree.SubElement(root, "NIFEmisor").text = self.company_id.vat or ""
        etree.SubElement(root, "NumSerieFactura").text = inv.name or ""
        etree.SubElement(root, "FechaExpedicion").text = (inv.invoice_date or date.today()).strftime("%d-%m-%Y")
        etree.SubElement(root, "ImporteTotal").text = "%.2f" % (inv.amount_total or 0.0)
        etree.SubElement(root, "Huella").text = rhash
        etree.SubElement(root, "HuellaAnterior").text = prev_hash
        try:
            etree.indent(root, space="  ")
        except AttributeError:
            pass
        xml_bytes = etree.tostring(root, xml_declaration=True, encoding="UTF-8")
        fname = "VeriFactu_%s.xml" % (inv.name or "INV").replace("/", "_")
        self.write({
            "file_name": fname,
            "file_data": base64.b64encode(xml_bytes).decode("ascii"),
            "generated_at": fields.Datetime.now(),
            "previous_hash": prev_hash,
            "record_hash": rhash,
            "qr_data": qr,
        })

    def action_mark_sent(self):
        self.write({"state": "sent"})
        self._log(_("Marquée envoyée."))

    def action_mark_accepted(self):
        self.write({"state": "accepted"})
        self._log(_("Acceptée."))

    def action_mark_rejected(self):
        self.write({"state": "rejected"})
        self._log(_("Refusée."))

    def _log(self, msg):
        now = fields.Datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for rec in self:
            prev = rec.status_note or ""
            rec.status_note = ("[%s] %s\n%s" % (now, msg, prev)).strip()
