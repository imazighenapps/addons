# -*- coding: utf-8 -*-
"""Document XRechnung (CIUS DE) : génération XML et suivi."""
import base64
from datetime import date

from lxml import etree

from odoo import _, api, fields, models
from odoo.exceptions import UserError

XR_NS = "urn:cen.eu:en16931:2017"
RSM = "urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100"
RAM = "urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100"
UDT = "urn:un:unece:uncefact:data:standard:UnqualifiedDataType:100"

STATES = [
    ("draft", "Brouillon"), ("ready", "Prête"), ("sent", "Envoyée"),
    ("accepted", "Acceptée"), ("rejected", "Refusée"),
]


class XRechnungDocument(models.Model):
    _name = "xrechnung.document"
    _description = "Document XRechnung (e-invoicing DE)"
    _inherit = ["mail.thread"]
    _order = "create_date desc, id desc"

    name = fields.Char(string="Référence", default="Nouveau", readonly=True, copy=False)
    company_id = fields.Many2one("res.company", required=True, default=lambda self: self.env.company)
    invoice_id = fields.Many2one(
        "account.move", string="Facture", required=True,
        domain="[('move_type','in',['out_invoice','out_refund']),('company_id','=',company_id),('state','=','posted')]")
    partner_id = fields.Many2one(related="invoice_id.partner_id", store=True)
    buyer_reference = fields.Char(string="Leitweg-ID / Buyer reference")
    state = fields.Selection(STATES, default="draft", tracking=True)
    file_name = fields.Char(readonly=True)
    file_data = fields.Binary(string="XRechnung XML", readonly=True)
    generated_at = fields.Datetime(readonly=True)
    validation_note = fields.Text(string="Contrôles", readonly=True)
    status_note = fields.Text(string="Journal des statuts", tracking=True)

    _sql_constraints = [("xrechnung_invoice_uniq", "unique(invoice_id)", "Document déjà existant pour cette facture.")]

    def action_validate(self):
        for rec in self:
            rec.validation_note = rec._run_checks() or _("Contrôles OK.")

    def _run_checks(self):
        self.ensure_one()
        inv = self.invoice_id
        issues = []
        if not inv.partner_id:
            issues.append(_("Client manquant."))
        if not (inv.invoice_date):
            issues.append(_("Date de facture manquante."))
        if not inv.invoice_line_ids:
            issues.append(_("Aucune ligne de facture."))
        if not self.company_id.vat:
            issues.append(_("TVA société manquante."))
        return "\n".join(issues)

    def action_generate(self):
        for rec in self:
            errs = rec._run_checks()
            if errs:
                raise UserError(_("Contrôles bloquants :\n%s") % errs)
            rec._generate_xml()
            rec.state = "ready"
            rec._log(_("XML XRechnung généré."))

    def _generate_xml(self):
        self.ensure_one()
        inv = self.invoice_id
        nsmap = {"rsm": RSM, "ram": RAM, "udt": UDT}
        root = etree.Element("{%s}CrossIndustryInvoice" % RSM, nsmap=nsmap)
        ctx = etree.SubElement(root, "{%s}ExchangedDocumentContext" % RSM)
        guide = etree.SubElement(ctx, "{%s}GuidelineSpecifiedDocumentContextParameter" % RAM)
        etree.SubElement(guide, "{%s}ID" % RAM).text = "urn:cen.eu:en16931:2017#compliant#urn:xoev-de:kosit:standard:xrechnung_2.3"
        doc = etree.SubElement(root, "{%s}ExchangedDocument" % RSM)
        etree.SubElement(doc, "{%s}ID" % RAM).text = inv.name or "INV"
        etree.SubElement(doc, "{%s}TypeCode" % RAM).text = "380" if inv.move_type == "out_invoice" else "381"
        issue = etree.SubElement(doc, "{%s}IssueDateTime" % RAM)
        etree.SubElement(issue, "{%s}DateTimeString" % UDT, format="102").text = (inv.invoice_date or date.today()).strftime("%Y%m%d")

        tx = etree.SubElement(root, "{%s}SupplyChainTradeTransaction" % RSM)
        for idx, line in enumerate(inv.invoice_line_ids, start=1):
            li = etree.SubElement(tx, "{%s}IncludedSupplyChainTradeLineItem" % RAM)
            docline = etree.SubElement(li, "{%s}AssociatedDocumentLineDocument" % RAM)
            etree.SubElement(docline, "{%s}LineID" % RAM).text = str(idx)
            prod = etree.SubElement(li, "{%s}SpecifiedTradeProduct" % RAM)
            etree.SubElement(prod, "{%s}Name" % RAM).text = line.name or "Item"
            agr = etree.SubElement(li, "{%s}SpecifiedLineTradeAgreement" % RAM)
            price = etree.SubElement(agr, "{%s}NetPriceProductTradePrice" % RAM)
            etree.SubElement(price, "{%s}ChargeAmount" % RAM).text = "%.2f" % (line.price_unit or 0.0)
            deliv = etree.SubElement(li, "{%s}SpecifiedLineTradeDelivery" % RAM)
            etree.SubElement(deliv, "{%s}BilledQuantity" % RAM, unitCode="C62").text = "%.2f" % (line.quantity or 0.0)
            sett = etree.SubElement(li, "{%s}SpecifiedLineTradeSettlement" % RAM)
            summ = etree.SubElement(sett, "{%s}SpecifiedTradeSettlementLineMonetarySummation" % RAM)
            etree.SubElement(summ, "{%s}LineTotalAmount" % RAM).text = "%.2f" % (line.price_subtotal or 0.0)

        hdr_agr = etree.SubElement(tx, "{%s}ApplicableHeaderTradeAgreement" % RAM)
        if self.buyer_reference:
            etree.SubElement(hdr_agr, "{%s}BuyerReference" % RAM).text = self.buyer_reference
        seller = etree.SubElement(hdr_agr, "{%s}SellerTradeParty" % RAM)
        etree.SubElement(seller, "{%s}Name" % RAM).text = self.company_id.name or ""
        buyer = etree.SubElement(hdr_agr, "{%s}BuyerTradeParty" % RAM)
        etree.SubElement(buyer, "{%s}Name" % RAM).text = inv.partner_id.name or ""

        hdr_set = etree.SubElement(tx, "{%s}ApplicableHeaderTradeSettlement" % RAM)
        etree.SubElement(hdr_set, "{%s}InvoiceCurrencyCode" % RAM).text = inv.currency_id.name or "EUR"
        totals = etree.SubElement(hdr_set, "{%s}SpecifiedTradeSettlementHeaderMonetarySummation" % RAM)
        etree.SubElement(totals, "{%s}LineTotalAmount" % RAM).text = "%.2f" % (inv.amount_untaxed or 0.0)
        etree.SubElement(totals, "{%s}TaxBasisTotalAmount" % RAM).text = "%.2f" % (inv.amount_untaxed or 0.0)
        etree.SubElement(totals, "{%s}TaxTotalAmount" % RAM, currencyID=inv.currency_id.name or "EUR").text = "%.2f" % (inv.amount_tax or 0.0)
        etree.SubElement(totals, "{%s}GrandTotalAmount" % RAM).text = "%.2f" % (inv.amount_total or 0.0)
        etree.SubElement(totals, "{%s}DuePayableAmount" % RAM).text = "%.2f" % (inv.amount_residual or inv.amount_total or 0.0)

        try:
            etree.indent(root, space="  ")
        except AttributeError:
            pass
        xml_bytes = etree.tostring(root, xml_declaration=True, encoding="UTF-8")
        fname = "XRechnung_%s.xml" % (inv.name or "INV").replace("/", "_")
        self.write({"file_name": fname, "file_data": base64.b64encode(xml_bytes).decode("ascii"),
                    "generated_at": fields.Datetime.now(), "validation_note": _("Contrôles OK.")})

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
