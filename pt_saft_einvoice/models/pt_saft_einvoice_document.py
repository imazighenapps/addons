# -*- coding: utf-8 -*-
import base64
import hashlib
import json
from datetime import date

from lxml import etree

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

STATES = [
    ("draft", "Brouillon"), ("ready", "Prête"), ("sent", "Envoyée"),
    ("accepted", "Acceptée"), ("rejected", "Refusée"),
]


class PtSaftDocument(models.Model):
    _name = "pt.saft.einvoice.document"
    _description = "SAF-T Fact Portugal (ATCUD/QR)"
    _inherit = ["mail.thread"]
    _order = "create_date desc, id desc"

    name = fields.Char(string="Référence", default="Nouveau", readonly=True, copy=False)
    company_id = fields.Many2one("res.company", required=True, default=lambda self: self.env.company)
    period_start = fields.Date(string="Début période")
    period_end = fields.Date(string="Fin période")
    invoice_id = fields.Many2one(
        "account.move", string="Facture liée", required=True,
        domain="[('move_type','in',['out_invoice','out_refund']),('company_id','=',company_id),('state','=','posted')]")
    state = fields.Selection(STATES, default="draft", tracking=True)
    file_name = fields.Char(string="Nom du fichier", readonly=True)
    file_data = fields.Binary(string="Fichier", readonly=True)
    generated_at = fields.Datetime(string="Généré le", readonly=True)
    external_id = fields.Char(string="Identifiant externe", tracking=True)
    summary_note = fields.Text(string="Détails", readonly=True)
    status_note = fields.Text(string="Journal des statuts", readonly=True)
    atcud_code = fields.Char(string="ATCUD", readonly=True)
    qr_payload = fields.Text(string="QR code", readonly=True)
    total_amount = fields.Monetary(string="Montant total", readonly=True)
    currency_id = fields.Many2one(related="company_id.currency_id", readonly=True)

    _sql_constraints = [("pt_saft_einvoice_document_invoice_uniq", "unique(invoice_id)", "Document déjà existant pour cette facture.")]

    def action_generate(self):
        for rec in self:
            rec._ensure_name("pt.saft.einvoice")
            rec._generate()
            rec.state = "ready"
            rec._log(_("SAF-T Fact / ATCUD / QR générés."))

    def _generate(self):
        self.ensure_one()
        inv = self.invoice_id
        atcud = "ATCUD-%s-%s" % ((inv.journal_id.code or "J"), (inv.name or "0").replace("/", ""))
        qr = "A:%s*B:%s*C:%s*D:%s*E:%s*F:%s*G:%s*H:%s*N:%.2f*O:%.2f" % (
            self.company_id.vat or "", inv.partner_id.vat or "", inv.partner_id.country_id.code or "PT",
            inv.move_type, "N", (inv.invoice_date or date.today()).strftime("%Y%m%d"),
            inv.name or "", atcud, inv.amount_untaxed or 0.0, inv.amount_tax or 0.0)
        root = etree.Element("AuditFile")
        hdr = etree.SubElement(root, "Header")
        etree.SubElement(hdr, "AuditFileVersion").text = "1.04_01"
        etree.SubElement(hdr, "CompanyID").text = self.company_id.vat or ""
        etree.SubElement(hdr, "CompanyName").text = self.company_id.name or ""
        master = etree.SubElement(root, "SourceDocuments")
        sales = etree.SubElement(master, "SalesInvoices")
        inv_el = etree.SubElement(sales, "Invoice")
        etree.SubElement(inv_el, "InvoiceNo").text = inv.name or ""
        etree.SubElement(inv_el, "ATCUD").text = atcud
        etree.SubElement(inv_el, "Hash").text = hashlib.sha256((inv.name or "").encode()).hexdigest()[:32]
        etree.SubElement(inv_el, "InvoiceDate").text = (inv.invoice_date or date.today()).strftime("%Y-%m-%d")
        etree.SubElement(inv_el, "GrossTotal").text = "%.2f" % (inv.amount_total or 0.0)
        etree.SubElement(inv_el, "QRCode").text = qr
        try:
            etree.indent(root, space="  ")
        except AttributeError:
            pass
        xml = etree.tostring(root, xml_declaration=True, encoding="UTF-8")
        fname = "SAFT_PT_%s.xml" % (inv.name or "INV").replace("/", "_")
        summary = _("ATCUD: %s | Montant: %.2f %s") % (atcud, inv.amount_total or 0.0, inv.currency_id.name or "EUR")
        self.write({"atcud_code": atcud, "qr_payload": qr, "total_amount": inv.amount_total})
        self._set_file(fname, xml, summary)

    def action_mark_sent(self):
        for rec in self:
            if rec.state not in ("ready", "rejected"):
                raise UserError(_("Le document doit être prêt ou refusé pour être envoyé."))
            rec._log(_("Marqué comme envoyé."))
            rec.state = "sent"

    def action_mark_accepted(self):
        self.write({"state": "accepted"})
        self._log(_("Acceptée."))

    def action_mark_rejected(self):
        self.write({"state": "rejected"})
        self._log(_("Refusée."))

    def action_reset(self):
        self.write({"state": "draft", "file_data": False, "file_name": False})

    def _log(self, msg):
        now = fields.Datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for rec in self:
            prev = rec.status_note or ""
            rec.status_note = ("[%s] %s\n%s" % (now, msg, prev)).strip()

    def _ensure_name(self, code):
        for rec in self:
            if not rec.name or rec.name in (_("Nouveau"), "Nouveau"):
                rec.name = self.env["ir.sequence"].next_by_code(code) or rec.name

    def _set_file(self, fname, content_bytes, summary=""):
        self.write({
            "file_name": fname,
            "file_data": base64.b64encode(content_bytes).decode("ascii"),
            "generated_at": fields.Datetime.now(),
            "summary_note": summary,
        })
