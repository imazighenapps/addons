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


class MxCfdiDocument(models.Model):
    _name = "mx.cfdi.document"
    _description = "CFDI 4.0 Mexique"
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
    external_id = fields.Char(string="UUID CFDI", tracking=True)
    summary_note = fields.Text(string="Détails", readonly=True)
    status_note = fields.Text(string="Journal des statuts", readonly=True)
    sat_status = fields.Selection([("vigente","Vigente"),("cancelado","Cancelado"),("no_encontrado","No encontrado")], string="Statut SAT", default="vigente")
    cancel_reason = fields.Char(string="Motif annulation")

    _sql_constraints = [("mx_cfdi_document_invoice_uniq", "unique(invoice_id)", "Document déjà existant pour cette facture.")]

    def action_generate(self):
        for rec in self:
            rec._ensure_name("mx.cfdi.document")
            rec._generate()
            rec.state = "ready"
            rec._log(_("CFDI 4.0 généré (timbrage PAC simulé)."))

    def action_cancel_sat(self):
        for rec in self:
            rec.sat_status = "cancelado"
            rec._log(_("Annulation SAT demandée. Motif: %s") % (rec.cancel_reason or "-"))

    def _generate(self):
        self.ensure_one()
        inv = self.invoice_id
        uuid_val = hashlib.md5(((inv.name or "") + str(inv.id)).encode()).hexdigest()
        ns = "http://www.sat.gob.mx/cfd/4"
        root = etree.Element("{%s}Comprobante" % ns, Version="4.0", nsmap={"cfdi": ns})
        root.set("Serie", (inv.journal_id.code or "A")[:5])
        root.set("Folio", (inv.name or "0").split("/")[-1])
        root.set("Fecha", (inv.invoice_date or date.today()).strftime("%Y-%m-%dT12:00:00"))
        root.set("Total", "%.2f" % (inv.amount_total or 0.0))
        root.set("SubTotal", "%.2f" % (inv.amount_untaxed or 0.0))
        root.set("Moneda", inv.currency_id.name or "MXN")
        emisor = etree.SubElement(root, "{%s}Emisor" % ns, Rfc=(self.company_id.vat or "XAXX010101000"), Nombre=self.company_id.name or "")
        receptor = etree.SubElement(root, "{%s}Receptor" % ns, Rfc=(inv.partner_id.vat or "XAXX010101000"), Nombre=inv.partner_id.name or "")
        conceptos = etree.SubElement(root, "{%s}Conceptos" % ns)
        for line in inv.invoice_line_ids:
            etree.SubElement(conceptos, "{%s}Concepto" % ns, Cantidad="%.2f" % (line.quantity or 0.0),
                             Descripcion=(line.name or "Item")[:100], ValorUnitario="%.2f" % (line.price_unit or 0.0),
                             Importe="%.2f" % (line.price_subtotal or 0.0))
        comp = etree.SubElement(root, "{%s}Complemento" % ns)
        tfd = etree.SubElement(comp, "TimbreFiscalDigital", UUID=uuid_val)
        try:
            etree.indent(root, space="  ")
        except AttributeError:
            pass
        xml = etree.tostring(root, xml_declaration=True, encoding="UTF-8")
        fname = "CFDI_%s.xml" % (inv.name or "INV").replace("/", "_")
        self.write({"external_id": uuid_val, "sat_status": "vigente"})
        summary = _("UUID: %s | Statut SAT: Vigente | Total: %.2f") % (uuid_val, inv.amount_total or 0.0)
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
