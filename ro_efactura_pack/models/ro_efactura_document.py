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


class RoEfacturaDocument(models.Model):
    _name = "ro.efactura.document"
    _description = "RoEfacturaDocument"
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


    _sql_constraints = [("ro_efactura_document_invoice_uniq", "unique(invoice_id)", "Document déjà existant pour cette facture.")]

    def action_generate(self):
        for rec in self:
            if not rec.name or rec.name == _("Nouveau"):
                rec.name = self.env["ir.sequence"].next_by_code("ro.efactura.document") or "DOC"
            rec._generate_xml()
            rec.state = "ready"
            rec._log(_("Document généré."))

    def _generate_xml(self):
        self.ensure_one()
        inv = self.invoice_id
        root = etree.Element("Invoice")
        etree.SubElement(root, "ID").text = inv.name or ""
        etree.SubElement(root, "IssueDate").text = (inv.invoice_date or date.today()).strftime("%Y-%m-%d")
        etree.SubElement(root, "DocumentCurrencyCode").text = inv.currency_id.name or "EUR"
        sup = etree.SubElement(root, "AccountingSupplierParty")
        etree.SubElement(sup, "Name").text = self.company_id.name or ""
        etree.SubElement(sup, "VAT").text = self.company_id.vat or ""
        cust = etree.SubElement(root, "AccountingCustomerParty")
        etree.SubElement(cust, "Name").text = inv.partner_id.name or ""
        etree.SubElement(cust, "VAT").text = inv.partner_id.vat or ""
        for idx, line in enumerate(inv.invoice_line_ids, start=1):
            il = etree.SubElement(root, "InvoiceLine")
            etree.SubElement(il, "ID").text = str(idx)
            etree.SubElement(il, "Description").text = line.name or ""
            etree.SubElement(il, "Quantity").text = "%.2f" % (line.quantity or 0.0)
            etree.SubElement(il, "LineExtensionAmount").text = "%.2f" % (line.price_subtotal or 0.0)
        tax = etree.SubElement(root, "TaxTotal")
        etree.SubElement(tax, "TaxAmount").text = "%.2f" % (inv.amount_tax or 0.0)
        legal = etree.SubElement(root, "LegalMonetaryTotal")
        etree.SubElement(legal, "TaxExclusiveAmount").text = "%.2f" % (inv.amount_untaxed or 0.0)
        etree.SubElement(legal, "PayableAmount").text = "%.2f" % (inv.amount_total or 0.0)

        try:
            etree.indent(root, space="  ")
        except AttributeError:
            pass
        xml_bytes = etree.tostring(root, xml_declaration=True, encoding="UTF-8")
        fname = "eFactura_%s.xml" % (inv.name or "INV").replace("/", "_")
        self.write({"file_name": fname, "file_data": base64.b64encode(xml_bytes).decode("ascii"),
                    "generated_at": fields.Datetime.now()})

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
