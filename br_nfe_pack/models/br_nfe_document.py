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


class BrNfeDocument(models.Model):
    _name = "br.nfe.document"
    _description = "NF-e Brésil"
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
    external_id = fields.Char(string="Chave NF-e", tracking=True)
    summary_note = fields.Text(string="Détails", readonly=True)
    status_note = fields.Text(string="Journal des statuts", readonly=True)
    protocol_number = fields.Char(string="Protocole SEFAZ", readonly=True)
    cce_count = fields.Integer(string="CC-e", default=0)

    _sql_constraints = [("br_nfe_document_invoice_uniq", "unique(invoice_id)", "Document déjà existant pour cette facture.")]

    def action_generate(self):
        for rec in self:
            rec._ensure_name("br.nfe.document")
            rec._generate()
            rec.state = "ready"
            rec._log(_("XML NF-e généré (protocole en attente)."))

    def action_cce(self):
        for rec in self:
            rec.cce_count += 1
            rec._log(_("Carta de Correção (CC-e) #%s enregistrée.") % rec.cce_count)

    def _generate(self):
        self.ensure_one()
        inv = self.invoice_id
        chave = (hashlib.sha256(((inv.name or "") + str(inv.id)).encode()).hexdigest()[:44]).upper()
        root = etree.Element("NFe")
        inf = etree.SubElement(root, "infNFe", Id="NFe" + chave)
        ide = etree.SubElement(inf, "ide")
        etree.SubElement(ide, "nNF").text = (inv.name or "0").split("/")[-1]
        etree.SubElement(ide, "dhEmi").text = (inv.invoice_date or date.today()).strftime("%Y-%m-%dT00:00:00-03:00")
        emit = etree.SubElement(inf, "emit")
        etree.SubElement(emit, "xNome").text = self.company_id.name or ""
        etree.SubElement(emit, "CNPJ").text = (self.company_id.vat or "").replace(".", "").replace("/", "").replace("-", "")
        dest = etree.SubElement(inf, "dest")
        etree.SubElement(dest, "xNome").text = inv.partner_id.name or ""
        for idx, line in enumerate(inv.invoice_line_ids, start=1):
            det = etree.SubElement(inf, "det", nItem=str(idx))
            prod = etree.SubElement(det, "prod")
            etree.SubElement(prod, "xProd").text = line.name or ""
            etree.SubElement(prod, "vProd").text = "%.2f" % (line.price_subtotal or 0.0)
        total = etree.SubElement(inf, "total")
        icms = etree.SubElement(total, "ICMSTot")
        etree.SubElement(icms, "vNF").text = "%.2f" % (inv.amount_total or 0.0)
        try:
            etree.indent(root, space="  ")
        except AttributeError:
            pass
        xml = etree.tostring(root, xml_declaration=True, encoding="UTF-8")
        fname = "NFe_%s.xml" % (inv.name or "INV").replace("/", "_")
        self.write({"external_id": chave})
        summary = _("Chave: %s | Total: %.2f") % (chave, inv.amount_total or 0.0)
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
