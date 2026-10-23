# -*- coding: utf-8 -*-
import base64
import csv
import io
import logging
from xml.etree import ElementTree as ET

from odoo import api, fields, models, _
from odoo.exceptions import UserError

from .fr_tools import clean_identifier, is_siren, is_siret, is_fr_vat

_logger = logging.getLogger(__name__)

FACTURX_CONTEXT = "urn:cen.eu:en16931:2017#conformant#urn:factur-x.eu:1p0:en16931"
NS = {
    "rsm": "urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100",
    "ram": "urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100",
    "udt": "urn:un:unece:uncefact:data:standard:UnqualifiedDataType:100",
}
for _prefix, _uri in NS.items():
    ET.register_namespace(_prefix, _uri)


def _el(parent, tag, text=None, attrib=None):
    node = ET.SubElement(parent, tag, attrib or {})
    if text is not None:
        node.text = text
    return node


class AccountMove(models.Model):
    _inherit = "account.move"

    fr_operation_type = fields.Selection(
        [
            ("goods", "Goods delivery"),
            ("services", "Services"),
            ("mixed", "Mixed goods and services"),
        ],
        string="Operation Type",
        help="Mandatory e-invoicing mention: nature of the invoiced operations.",
    )
    fr_validation_state = fields.Selection(
        [
            ("todo", "To Check"),
            ("ok", "Compliant"),
            ("error", "Non-Compliant"),
        ],
        string="EN16931 Check",
        default="todo",
        copy=False,
    )
    fr_validation_report = fields.Text(string="Validation Report", copy=False)
    fr_ereport_status = fields.Selection(
        [
            ("none", "Not Concerned"),
            ("ready", "Ready"),
            ("sent", "Sent"),
            ("done", "Completed"),
            ("error", "Error"),
        ],
        string="E-Reporting",
        default="none",
        copy=False,
    )
    fr_chorus_status = fields.Selection(
        [
            ("none", "Not Sent"),
            ("sent", "Submitted"),
            ("accepted", "Accepted"),
            ("rejected", "Rejected"),
            ("error", "Error"),
        ],
        string="Chorus Pro",
        default="none",
        copy=False,
    )
    fr_ereport_line_ids = fields.One2many(
        "fr.ereport.line", "move_id", string="E-Reporting Lines"
    )

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    def _fr_collect_issues(self):
        """Return a list of (severity, message) tuples for EN16931 checks."""
        self.ensure_one()
        issues = []
        move = self
        if move.move_type not in ("out_invoice", "out_refund"):
            return issues
        company = move.company_id
        partner = move.commercial_partner_id
        if company.country_id.code != "FR" and (not partner.country_id or partner.country_id.code != "FR"):
            return issues
        if not is_siret(company.partner_id.fr_siret) and not is_siren(company.partner_id.fr_siren):
            issues.append(("error", _("Company is missing a valid SIREN/SIRET.")))
        if partner.country_id.code == "FR":
            if not is_siren(partner.fr_siren):
                issues.append(("error", _("Customer is missing a valid SIREN (new mandatory mention).")))
            if partner.vat and not is_fr_vat(partner.vat):
                issues.append(("error", _("Customer VAT number is not a valid French VAT number.")))
        else:
            if not partner.vat and not partner.fr_siren:
                issues.append(("warning", _("Foreign customer has neither VAT number nor SIREN.")))
        if not move.fr_operation_type:
            issues.append(("error", _("Operation type is required (goods / services / mixed).")))
        if not move.invoice_date:
            issues.append(("error", _("Invoice date is required.")))
        if not move.invoice_line_ids:
            issues.append(("error", _("The invoice has no lines.")))
        for line in move.invoice_line_ids:
            if not line.product_id and not line.name:
                issues.append(("error", _("A line has neither product nor label.")))
            if len(line.tax_ids) != 1:
                issues.append((
                    "error",
                    _("Each line must carry exactly one tax for e-invoicing (line: %s).") % (line.name or "?"),
                ))
        expected_total = round(move.amount_untaxed + move.amount_tax, 2)
        if abs(expected_total - round(move.amount_total, 2)) > 0.015:
            issues.append(("error", _("Totals are inconsistent (untaxed + tax != total).")))
        if move.amount_total <= 0 and move.move_type == "out_invoice":
            issues.append(("warning", _("Invoice total is not positive.")))
        return issues

    def action_fr_validate(self):
        self.ensure_one()
        issues = self._fr_collect_issues()
        errors = [msg for sev, msg in issues if sev == "error"]
        self.write({
            "fr_validation_state": "error" if errors else "ok",
            "fr_validation_report": "\n".join(
                ["[%s] %s" % (sev.upper(), msg) for sev, msg in issues]
            ) or _("No issue detected."),
        })
        return True

    def action_post(self):
        block = self.env["ir.config_parameter"].sudo().get_param(
            "fr_einvoicing_pack.block_noncompliant", "True"
        ) not in ("False", "false", "0", "")
        for move in self.filtered(lambda m: m.move_type in ("out_invoice", "out_refund")):
            issues = move._fr_collect_issues()
            errors = [msg for sev, msg in issues if sev == "error"]
            move.write({
                "fr_validation_state": "error" if errors else "ok",
                "fr_validation_report": "\n".join(
                    ["[%s] %s" % (sev.upper(), msg) for sev, msg in issues]
                ) or _("No issue detected."),
            })
            if errors and block:
                raise UserError(
                    _("E-invoicing validation failed for %s:\n%s")
                    % (move.name or _("draft invoice"), "\n- " + "\n- ".join(errors))
                )
        res = super().action_post()
        self._fr_register_ereport()
        return res

    # ------------------------------------------------------------------
    # E-reporting register
    # ------------------------------------------------------------------
    def _fr_register_ereport(self):
        enabled = self.env["ir.config_parameter"].sudo().get_param(
            "fr_einvoicing_pack.ereport_enabled", "True"
        ) not in ("False", "false", "0", "")
        if not enabled:
            return
        lines = self.env["fr.ereport.line"]
        for move in self.filtered(lambda m: m.state == "posted" and m.move_type in ("out_invoice", "out_refund")):
            partner = move.commercial_partner_id
            if partner.country_id.code == "FR":
                flow = "einvoice_b2b"
            elif partner.country_id:
                flow = "ereport_intl"
            else:
                flow = "ereport_b2c"
            lines |= self.env["fr.ereport.line"].create({
                "name": _("E-report %s") % (move.name or move.ref or "?"),
                "move_id": move.id,
                "partner_id": partner.id,
                "company_id": move.company_id.id,
                "flow": flow,
                "amount_total": move.amount_total,
                "currency_id": move.currency_id.id,
                "status": "ready",
            })
            move.fr_ereport_status = "ready"

    def action_fr_export_ereport_csv(self):
        self.ensure_one()
        rows = [["reference", "flow", "partner", "amount", "currency", "status"]]
        for line in self.fr_ereport_line_ids:
            rows.append([
                line.name, line.flow,
                line.partner_id.display_name,
                str(line.amount_total),
                line.currency_id.name or "",
                line.status,
            ])
        buffer = io.StringIO()
        csv.writer(buffer).writerows(rows)
        attachment = self.env["ir.attachment"].create({
            "name": "ereport_%s.csv" % (self.name or "draft"),
            "raw": base64.b64encode(buffer.getvalue().encode("utf-8")),
            "res_model": self._name,
            "res_id": self.id,
            "mimetype": "text/csv",
        })
        return {
            "type": "ir.actions.act_url",
            "url": "/web/content/%s?download=true" % attachment.id,
            "target": "self",
        }

    # ------------------------------------------------------------------
    # Factur-X (EN16931 profile) generation
    # ------------------------------------------------------------------
    def action_fr_generate_facturx(self):
        self.ensure_one()
        xml_bytes = self._fr_build_facturx()
        attachment = self.env["ir.attachment"].create({
            "name": "%s_facturx.xml" % (self.name or "invoice"),
            "raw": base64.b64encode(xml_bytes),
            "res_model": self._name,
            "res_id": self.id,
            "mimetype": "application/xml",
        })
        return {
            "type": "ir.actions.act_url",
            "url": "/web/content/%s?download=true" % attachment.id,
            "target": "self",
        }

    def _fr_build_facturx(self):
        self.ensure_one()
        move = self
        company = move.company_id
        partner = move.commercial_partner_id
        root = ET.Element("{%s}CrossIndustryInvoice" % NS["rsm"])
        ctx = _el(root, "{%s}ExchangedDocumentContext" % NS["rsm"])
        _el(ctx, "{%s}GuidelineSpecifiedDocumentContextParameter" % NS["ram"],
            attrib={"{%s}ID" % NS["ram"]: FACTURX_CONTEXT})
        doc = _el(root, "{%s}ExchangedDocument" % NS["rsm"])
        _el(doc, "{%s}ID" % NS["ram"], move.name or move.ref or "DRAFT")
        _el(doc, "{%s}TypeCode" % NS["ram"], "380" if move.move_type == "out_invoice" else "381")
        issue = _el(doc, "{%s}IssueDateTime" % NS["ram"])
        _el(issue, "{%s}DateTimeString" % NS["udt"],
            (move.invoice_date or fields.Date.today()).strftime("%Y%m%d"),
            attrib={"format": "102"})
        txn = _el(root, "{%s}SupplyChainTradeTransaction" % NS["rsm"])
        for idx, line in enumerate(move.invoice_line_ids, start=1):
            item = _el(txn, "{%s}IncludedSupplyChainTradeLineItem" % NS["ram"])
            doc_line = _el(item, "{%s}AssociatedDocumentLineDocument" % NS["ram"])
            _el(doc_line, "{%s}LineID" % NS["ram"], str(idx))
            delivery = _el(item, "{%s}SpecifiedLineTradeDelivery" % NS["ram"])
            _el(delivery, "{%s}BilledQuantity" % NS["ram"], str(line.quantity),
                attrib={"unitCode": "C62"})
            settlement = _el(item, "{%s}SpecifiedLineTradeSettlement" % NS["ram"])
            trade_tax = _el(settlement, "{%s}ApplicableTradeTax" % NS["ram"])
            tax = line.tax_ids[:1]
            _el(trade_tax, "{%s}TypeCode" % NS["ram"], "VAT")
            _el(trade_tax, "{%s}CategoryCode" % NS["ram"], "S")
            _el(trade_tax, "{%s}RateApplicablePercent" % NS["ram"], str(tax.amount if tax else 0))
            monetary = _el(settlement, "{%s}SpecifiedTradeSettlementLineMonetarySummation" % NS["ram"])
            _el(monetary, "{%s}LineTotalAmount" % NS["ram"], "%.2f" % line.price_subtotal)
            product = _el(item, "{%s}SpecifiedTradeProduct" % NS["ram"])
            _el(product, "{%s}Name" % NS["ram"], (line.name or (line.product_id.display_name if line.product_id else "?"))[:200])
        header = _el(txn, "{%s}ApplicableHeaderTradeAgreement" % NS["ram"])
        seller = _el(header, "{%s}SellerTradeParty" % NS["ram"])
        _el(seller, "{%s}Name" % NS["ram"], company.name)
        seller_org = _el(seller, "{%s}SpecifiedLegalOrganization" % NS["ram"])
        _el(seller_org, "{%s}ID" % NS["ram"],
            clean_identifier(company.partner_id.fr_siret or company.partner_id.fr_siren or ""),
            attrib={"schemeID": "0002"})
        seller_tax = _el(seller, "{%s}SpecifiedTaxRegistration" % NS["ram"])
        _el(seller_tax, "{%s}ID" % NS["ram"], company.partner_id.vat or "",
            attrib={"schemeID": "VA"})
        buyer = _el(header, "{%s}BuyerTradeParty" % NS["ram"])
        _el(buyer, "{%s}Name" % NS["ram"], partner.name)
        buyer_org = _el(buyer, "{%s}SpecifiedLegalOrganization" % NS["ram"])
        _el(buyer_org, "{%s}ID" % NS["ram"], clean_identifier(partner.fr_siret or partner.fr_siren or ""),
            attrib={"schemeID": "0002"})
        if partner.vat:
            buyer_tax = _el(buyer, "{%s}SpecifiedTaxRegistration" % NS["ram"])
            _el(buyer_tax, "{%s}ID" % NS["ram"], partner.vat, attrib={"schemeID": "VA"})
        delivery = _el(txn, "{%s}ApplicableHeaderTradeDelivery" % NS["ram"])
        settlement = _el(txn, "{%s}ApplicableHeaderTradeSettlement" % NS["ram"])
        _el(settlement, "{%s}InvoiceCurrencyCode" % NS["ram"], move.currency_id.name or "EUR")
        by_rate = {}
        for line in move.invoice_line_ids:
            tax = line.tax_ids[:1]
            rate = tax.amount if tax else 0.0
            key = round(rate, 2)
            bucket = by_rate.setdefault(key, {"basis": 0.0, "tax": 0.0})
            bucket["basis"] += line.price_subtotal
            bucket["tax"] += line.price_subtotal * rate / 100.0
        for rate in sorted(by_rate):
            trade_tax = _el(settlement, "{%s}ApplicableTradeTax" % NS["ram"])
            _el(trade_tax, "{%s}CalculatedAmount" % NS["ram"], "%.2f" % by_rate[rate]["tax"])
            _el(trade_tax, "{%s}TypeCode" % NS["ram"], "VAT")
            _el(trade_tax, "{%s}BasisAmount" % NS["ram"], "%.2f" % by_rate[rate]["basis"])
            _el(trade_tax, "{%s}CategoryCode" % NS["ram"], "S")
            _el(trade_tax, "{%s}RateApplicablePercent" % NS["ram"], str(rate))
        summary = _el(settlement, "{%s}SpecifiedTradeSettlementHeaderMonetarySummation" % NS["ram"])
        _el(summary, "{%s}LineTotalAmount" % NS["ram"], "%.2f" % move.amount_untaxed)
        _el(summary, "{%s}TaxBasisTotalAmount" % NS["ram"], "%.2f" % move.amount_untaxed)
        _el(summary, "{%s}TaxTotalAmount" % NS["ram"], "%.2f" % move.amount_tax,
            attrib={"currencyID": move.currency_id.name or "EUR"})
        _el(summary, "{%s}GrandTotalAmount" % NS["ram"], "%.2f" % move.amount_total)
        _el(summary, "{%s}DuePayableAmount" % NS["ram"], "%.2f" % move.amount_residual)
        return ET.tostring(root, encoding="utf-8", xml_declaration=True)

    # ------------------------------------------------------------------
    # Chorus Pro connector
    # ------------------------------------------------------------------
    def action_fr_send_chorus(self):
        self.ensure_one()
        params = self.env["ir.config_parameter"].sudo()
        url = params.get_param("fr_einvoicing_pack.chorus_url")
        login = params.get_param("fr_einvoicing_pack.chorus_login")
        if not url or not login:
            raise UserError(_("Please configure the Chorus Pro API URL and login in Accounting settings first."))
        payload = {
            "siret": clean_identifier(self.company_id.partner_id.fr_siret),
            "invoice_number": self.name,
            "invoice_date": str(self.invoice_date or ""),
            "customer_siret": clean_identifier(self.commercial_partner_id.fr_siret),
            "amount_untaxed": self.amount_untaxed,
            "amount_tax": self.amount_tax,
            "amount_total": self.amount_total,
            "currency": self.currency_id.name,
        }
        try:
            import requests
            response = requests.post(url, json=payload, timeout=25)
            ok = 200 <= response.status_code < 300
        except Exception as exc:
            _logger.warning("Chorus Pro submission failed: %s", exc)
            self.write({"fr_chorus_status": "error"})
            self.env["fr.ereport.line"].create({
                "name": _("Chorus %s") % (self.name or "?"),
                "move_id": self.id,
                "partner_id": self.commercial_partner_id.id,
                "company_id": self.company_id.id,
                "flow": "chorus",
                "amount_total": self.amount_total,
                "currency_id": self.currency_id.id,
                "status": "error",
                "message": str(exc),
            })
            raise UserError(_("Chorus Pro submission failed: %s") % exc)
        self.write({"fr_chorus_status": "sent" if ok else "error"})
        return True

