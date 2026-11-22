# -*- coding: utf-8 -*-
"""Document e-invoicing SdI (FatturaPA) : génération XML et suivi des statuts."""
import base64
from datetime import date

from lxml import etree

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

SDI_STATES = [
    ("draft", "Brouillon"),
    ("ready", "Prête"),
    ("sent", "Envoyée"),
    ("delivered", "Délivrée (NS/MC)"),
    ("accepted", "Acceptée"),
    ("rejected", "Refusée"),
]


class SdiDocument(models.Model):
    _name = "sdi.document"
    _description = "Document e-invoicing SdI (FatturaPA)"
    _inherit = ["mail.thread"]
    _order = "create_date desc, id desc"

    name = fields.Char(
        string="Référence", default="Nouveau", readonly=True, copy=False)
    company_id = fields.Many2one(
        "res.company", string="Société", required=True,
        default=lambda self: self.env.company)
    invoice_id = fields.Many2one(
        "account.move", string="Facture", required=True,
        domain="[('move_type','in',['out_invoice','out_refund']),"
               "('company_id','=',company_id),('state','=','posted')]")
    partner_id = fields.Many2one(
        related="invoice_id.partner_id", store=True, string="Client")
    destinatario_code = fields.Char(
        string="Codice destinatario", size=7, default="0000000",
        help="Code SdI du destinataire (7 caractères) ou 0000000 si PEC.")
    pec_address = fields.Char(string="PEC destinataire")
    transmission_format = fields.Selection(
        [("FPR12", "FPR12 (B2B/B2C)"), ("FPA12", "FPA12 (PA)")],
        string="Format", default="FPR12", required=True)
    state = fields.Selection(SDI_STATES, string="Statut", default="draft", tracking=True)
    file_name = fields.Char(string="Nom du fichier", readonly=True)
    file_data = fields.Binary(string="FatturaPA XML", readonly=True)
    generated_at = fields.Datetime(string="Généré le", readonly=True)
    sdi_identifier = fields.Char(string="Identifiant SdI", tracking=True)
    status_note = fields.Text(string="Journal des statuts", tracking=True)
    last_error = fields.Text(string="Dernière erreur")

    _sql_constraints = [
        ("sdi_document_invoice_uniq", "unique(invoice_id)",
         "Un document SdI existe déjà pour cette facture."),
    ]

    @api.constrains("destinatario_code")
    def _check_destinatario(self):
        for rec in self:
            code = (rec.destinatario_code or "").strip()
            if code and len(code) != 7:
                raise ValidationError(_(
                    "Le codice destinatario doit comporter 7 caractères."))

    def action_prepare(self):
        for rec in self:
            rec._generate_xml()
            rec._log_status(_("XML FatturaPA généré, document prêt."))
            rec.state = "ready"

    def _generate_xml(self):
        self.ensure_one()
        inv = self.invoice_id
        if inv.state != "posted":
            raise UserError(_("La facture doit être validée."))
        root = etree.Element(
            "{http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v1.2}"
            "FatturaElettronica",
            versione=self.transmission_format,
            nsmap={"p": "http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v1.2"})
        header = etree.SubElement(root, "{http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v1.2}FatturaElettronicaHeader")
        dati_trasm = etree.SubElement(header, "{http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v1.2}DatiTrasmissione")
        id_trasm = etree.SubElement(dati_trasm, "{http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v1.2}IdTrasmittente")
        etree.SubElement(id_trasm, "{http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v1.2}IdPaese").text = (self.company_id.country_id.code or "IT")
        etree.SubElement(id_trasm, "{http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v1.2}IdCodice").text = (self.company_id.vat or "00000000000")[-11:]
        etree.SubElement(dati_trasm, "{http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v1.2}ProgressivoInvio").text = (self.name or "00001")[-5:]
        etree.SubElement(dati_trasm, "{http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v1.2}FormatoTrasmissione").text = self.transmission_format
        etree.SubElement(dati_trasm, "{http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v1.2}CodiceDestinatario").text = (self.destinatario_code or "0000000").strip()
        if self.pec_address and (self.destinatario_code or "0000000").strip() == "0000000":
            etree.SubElement(dati_trasm, "{http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v1.2}PECDestinatario").text = self.pec_address

        cedente = etree.SubElement(header, "{http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v1.2}CedentePrestatore")
        dati_anag = etree.SubElement(cedente, "{http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v1.2}DatiAnagrafici")
        id_fisc = etree.SubElement(dati_anag, "{http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v1.2}IdFiscaleIVA")
        etree.SubElement(id_fisc, "{http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v1.2}IdPaese").text = (self.company_id.country_id.code or "IT")
        etree.SubElement(id_fisc, "{http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v1.2}IdCodice").text = (self.company_id.vat or "00000000000").replace("IT", "")[:11]
        anag = etree.SubElement(dati_anag, "{http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v1.2}Anagrafica")
        etree.SubElement(anag, "{http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v1.2}Denominazione").text = self.company_id.name or ""

        cessionario = etree.SubElement(header, "{http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v1.2}CessionarioCommittente")
        dati_anag_c = etree.SubElement(cessionario, "{http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v1.2}DatiAnagrafici")
        anag_c = etree.SubElement(dati_anag_c, "{http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v1.2}Anagrafica")
        etree.SubElement(anag_c, "{http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v1.2}Denominazione").text = inv.partner_id.name or ""

        body = etree.SubElement(root, "{http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v1.2}FatturaElettronicaBody")
        dati_gen = etree.SubElement(body, "{http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v1.2}DatiGenerali")
        dati_doc = etree.SubElement(dati_gen, "{http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v1.2}DatiGeneraliDocumento")
        etree.SubElement(dati_doc, "{http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v1.2}TipoDocumento").text = "TD01" if inv.move_type == "out_invoice" else "TD04"
        etree.SubElement(dati_doc, "{http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v1.2}Divisa").text = inv.currency_id.name or "EUR"
        etree.SubElement(dati_doc, "{http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v1.2}Data").text = (inv.invoice_date or date.today()).strftime("%Y-%m-%d")
        etree.SubElement(dati_doc, "{http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v1.2}Numero").text = inv.name or "INV"

        dati_beni = etree.SubElement(body, "{http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v1.2}DatiBeniServizi")
        for idx, line in enumerate(inv.invoice_line_ids, start=1):
            det = etree.SubElement(dati_beni, "{http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v1.2}DettaglioLinee")
            etree.SubElement(det, "{http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v1.2}NumeroLinea").text = str(idx)
            etree.SubElement(det, "{http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v1.2}Descrizione").text = line.name or "Linea"
            etree.SubElement(det, "{http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v1.2}PrezzoUnitario").text = "%.2f" % (line.price_unit or 0.0)
            etree.SubElement(det, "{http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v1.2}PrezzoTotale").text = "%.2f" % (line.price_subtotal or 0.0)
            rate = (line.tax_ids[0].amount if line.tax_ids else 0.0)
            etree.SubElement(det, "{http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v1.2}AliquotaIVA").text = "%.2f" % rate
        riepilogo = etree.SubElement(dati_beni, "{http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v1.2}DatiRiepilogo")
        etree.SubElement(riepilogo, "{http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v1.2}AliquotaIVA").text = "0.00"
        etree.SubElement(riepilogo, "{http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v1.2}ImponibileImporto").text = "%.2f" % (inv.amount_untaxed or 0.0)
        etree.SubElement(riepilogo, "{http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v1.2}Imposta").text = "%.2f" % (inv.amount_tax or 0.0)

        try:
            etree.indent(root, space="  ")
        except AttributeError:
            pass
        xml_bytes = etree.tostring(root, xml_declaration=True, encoding="UTF-8")
        fname = "IT_%s_%s.xml" % (
            (self.company_id.vat or "NOVAT").replace(" ", "")[:11],
            (inv.name or "INV").replace("/", "_"))
        self.write({
            "file_name": fname,
            "file_data": base64.b64encode(xml_bytes).decode("ascii"),
            "generated_at": fields.Datetime.now(),
        })

    def action_mark_sent(self):
        for rec in self:
            if rec.state not in ("ready", "rejected"):
                raise UserError(_("Le document doit être prêt ou refusé pour être envoyé."))
            rec._log_status(_("Marqué comme envoyé au SdI."))
            rec.state = "sent"

    def action_mark_delivered(self):
        for rec in self:
            rec._log_status(_("Accusé SdI : délivré (NS/MC)."))
            rec.state = "delivered"

    def action_mark_accepted(self):
        for rec in self:
            rec._log_status(_("Statut SdI : accepté."))
            rec.state = "accepted"

    def action_mark_rejected(self):
        for rec in self:
            rec._log_status(_("Statut SdI : refusé. %s") % (rec.last_error or ""))
            rec.state = "rejected"

    def action_reset(self):
        for rec in self:
            rec.write({"state": "draft", "file_data": False, "file_name": False,
                       "last_error": False})

    def _log_status(self, msg):
        now = fields.Datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for rec in self:
            prev = rec.status_note or ""
            rec.status_note = (("[%s] %s\n" % (now, msg)) + prev).strip()
