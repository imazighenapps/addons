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


class SaZatcaDocument(models.Model):
    _name = "sa.zatca.einvoice.document"
    _description = "e-Invoice ZATCA Phase 2"
    _inherit = ["mail.thread"]
    _order = "create_date desc, id desc"

    name = fields.Char(string="Référence", default="Nouveau", readonly=True, copy=False)
    company_id = fields.Many2one("res.company", required=True, default=lambda self: self.env.company)
    period_start = fields.Date(string="Début période")
    period_end = fields.Date(string="Fin période")
    invoice_id = fields.Many2one("account.move", string="Facture liée", required=True,
        domain="[('move_type','in',['out_invoice','out_refund']),('company_id','=',company_id),('state','=','posted')]")
    state = fields.Selection(STATES, default="draft", tracking=True)
    file_name = fields.Char(string="Nom du fichier", readonly=True)
    file_data = fields.Binary(string="Fichier", readonly=True)
    generated_at = fields.Datetime(string="Généré le", readonly=True)
    external_id = fields.Char(string="UUID ZATCA", tracking=True)
    summary_note = fields.Text(string="Détails", readonly=True)
    status_note = fields.Text(string="Journal des statuts", readonly=True)
    invoice_hash = fields.Char(string="Hash chaîné", readonly=True)
    previous_hash = fields.Char(string="Hash précédent", readonly=True)
    qr_data = fields.Text(string="QR TLV", readonly=True)

    _sql_constraints = [("sa_zatca_einvoice_document_invoice_uniq", "unique(invoice_id)", "Document déjà existant pour cette facture.")]

    def action_generate(self):
        for rec in self:
            rec._ensure_name("sa.zatca.einvoice")
            rec._generate()
            rec.state = "ready"
            rec._log(_("XML ZATCA généré (signature/hash préparés)."))

    def _generate(self):
        self.ensure_one()
        inv = self.invoice_id
        prev = self.search([("company_id","=",self.company_id.id),("id","!=",self.id),("invoice_hash","!=",False)], order="id desc", limit=1)
        prev_hash = prev.invoice_hash or ("0"*64)
        payload = "|".join([self.company_id.vat or "", inv.name or "", str(inv.amount_total or 0.0), prev_hash])
        ihash = hashlib.sha256(payload.encode()).hexdigest().upper()
        uuid_val = hashlib.md5((inv.name or str(inv.id)).encode()).hexdigest()
        qr = "SELLER:%s|VAT:%s|TIME:%s|TOTAL:%.2f|TAX:%.2f|HASH:%s" % (
            self.company_id.name or "", self.company_id.vat or "",
            fields.Datetime.now().strftime("%Y-%m-%dT%H:%M:%S"), inv.amount_total or 0.0, inv.amount_tax or 0.0, ihash[:16])
        root = etree.Element("Invoice")
        etree.SubElement(root, "UUID").text = uuid_val
        etree.SubElement(root, "InvoiceID").text = inv.name or ""
        etree.SubElement(root, "IssueDate").text = (inv.invoice_date or date.today()).strftime("%Y-%m-%d")
        sup = etree.SubElement(root, "Supplier")
        etree.SubElement(sup, "Name").text = self.company_id.name or ""
        etree.SubElement(sup, "VAT").text = self.company_id.vat or ""
        cust = etree.SubElement(root, "Customer")
        etree.SubElement(cust, "Name").text = inv.partner_id.name or ""
        etree.SubElement(cust, "VAT").text = inv.partner_id.vat or ""
        totals = etree.SubElement(root, "LegalMonetaryTotal")
        etree.SubElement(totals, "TaxExclusiveAmount").text = "%.2f" % (inv.amount_untaxed or 0.0)
        etree.SubElement(totals, "TaxInclusiveAmount").text = "%.2f" % (inv.amount_total or 0.0)
        etree.SubElement(totals, "PayableAmount").text = "%.2f" % (inv.amount_total or 0.0)
        sig = etree.SubElement(root, "SignatureInfo")
        etree.SubElement(sig, "InvoiceHash").text = ihash
        etree.SubElement(sig, "PreviousHash").text = prev_hash
        try:
            etree.indent(root, space="  ")
        except AttributeError:
            pass
        xml = etree.tostring(root, xml_declaration=True, encoding="UTF-8")
        fname = "ZATCA_%s.xml" % (inv.name or "INV").replace("/", "_")
        self.write({"invoice_hash": ihash, "previous_hash": prev_hash, "qr_data": qr, "external_id": uuid_val})
        summary = _("UUID: %s | Hash: %s…") % (uuid_val, ihash[:12])
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
