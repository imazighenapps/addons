# -*- coding: utf-8 -*-
import re
import xml.etree.ElementTree as ET

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

PAYABLE_PATTERN = r"cbc:PayableAmount[^>]*>([^<]*)<"


class EinvoiceCheck(models.Model):
    _name = "einvoice.check"
    _description = "E-Invoice Check"
    _inherit = ["mail.thread"]
    _order = "id desc"

    name = fields.Char(
        string="Reference", required=True, copy=False, tracking=True,
        help="Unique reference of the check, for example EINV/2026/00001.")
    invoice_id = fields.Many2one(
        "account.move", string="Invoice", required=True, tracking=True,
        ondelete="cascade", index=True,
        domain=[("move_type", "=", "out_invoice")],
        help="Posted customer invoice that is checked against the "
             "e-invoicing rules.")
    partner_id = fields.Many2one(
        related="invoice_id.partner_id", string="Customer",
        store=True, readonly=True)
    format = fields.Selection(
        [("facturx", "Factur-X"), ("ubl", "UBL"),
         ("xrechnung", "XRechnung")],
        string="Format", required=True, default="ubl",
        help="Target e-invoicing format of the generated XML document.")
    state = fields.Selection(
        [("draft", "Draft"), ("generated", "Generated"),
         ("valid", "Valid"), ("invalid", "Invalid")],
        string="Status", default="draft", required=True, copy=False,
        tracking=True, index=True,
        help="Generated means the XML document exists. Valid means the "
             "validation raised no error-class issue; warnings alone do "
             "not make a check invalid.")
    xml_data = fields.Text(
        string="Generated XML", copy=False, readonly=True,
        help="UBL-style XML document generated from the customer invoice.")
    issue_ids = fields.One2many(
        "einvoice.issue", "check_id", string="Issues", copy=False)
    issue_count = fields.Integer(
        string="Issue Count", compute="_compute_issue_count", store=True)
    note = fields.Text(string="Notes")
    company_id = fields.Many2one(
        "res.company", string="Company", required=True,
        default=lambda self: self.env.company, index=True)

    _sql_constraints = [
        ('name_company_uniq', "UNIQUE(name, company_id)", "The check reference must be unique per company."),
    ]

    @api.depends("issue_ids")
    def _compute_issue_count(self):
        for check in self:
            check.issue_count = len(check.issue_ids)

    @api.constrains("invoice_id")
    def _check_invoice_type(self):
        for check in self:
            if check.invoice_id and check.invoice_id.move_type != "out_invoice":
                raise ValidationError(_(
                    "An e-invoice check can only be attached to a customer "
                    "invoice, not to a vendor bill or another entry."))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("name") or vals["name"] == "/":
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "einvoice.check") or "/"
        return super().create(vals_list)

    def _replace_issues(self, issues):
        self.ensure_one()
        self.env["einvoice.issue"].search([
            ("check_id", "=", self.id)]).unlink()
        self.env["einvoice.issue"].create([
            dict(issue, check_id=self.id) for issue in issues])
        return True

    def _build_xml(self, invoice):
        self.ensure_one()
        currency = (invoice.currency_id.name
                    or invoice.company_id.currency_id.name or "EUR")
        untaxed = invoice.amount_untaxed or 0.0
        tax = invoice.amount_tax or 0.0
        total = invoice.amount_total or 0.0
        root = ET.Element("Invoice", {
            "xmlns": "urn:oasis:names:specification:ubl:schema:xsd:"
                     "Invoice-2",
            "xmlns:cac": "urn:oasis:names:specification:ubl:schema:xsd:"
                         "CommonAggregateComponents-2",
            "xmlns:cbc": "urn:oasis:names:specification:ubl:schema:xsd:"
                         "CommonBasicComponents-2",
        })

        def tag(parent, name, text=None, attrib=None):
            element = ET.SubElement(parent, name, attrib or {})
            if text is not None:
                element.text = text
            return element

        tag(root, "cbc:UBLVersionNumber", "2.1")
        tag(root, "cbc:CustomizationID", "urn:cen.eu:en16931-2017")
        tag(root, "cbc:ID", invoice.name or "NO-REFERENCE")
        tag(root, "cbc:IssueDate", fields.Date.to_string(
            invoice.invoice_date or fields.Date.today()))
        tag(root, "cbc:DocumentCurrencyCode", currency)
        supplier_party = tag(tag(root, "cac:AccountingSupplierParty"),
                             "cac:Party")
        tag(tag(supplier_party, "cac:PartyName"), "cbc:Name",
            invoice.company_id.name or "")
        customer_party = tag(tag(root, "cac:AccountingCustomerParty"),
                             "cac:Party")
        tag(tag(customer_party, "cac:PartyName"), "cbc:Name",
            invoice.partner_id.name or "")
        tax_total = tag(root, "cac:TaxTotal")
        tag(tax_total, "cbc:TaxAmount", "%.2f" % tax,
            {"currencyID": currency})
        monetary = tag(root, "cac:LegalMonetaryTotal")
        tag(monetary, "cbc:LineExtensionAmount", "%.2f" % untaxed,
            {"currencyID": currency})
        tag(monetary, "cbc:TaxExclusiveAmount", "%.2f" % untaxed,
            {"currencyID": currency})
        tag(monetary, "cbc:TaxInclusiveAmount", "%.2f" % total,
            {"currencyID": currency})
        tag(monetary, "cbc:PayableAmount", "%.2f" % total,
            {"currencyID": currency})
        for index, line in enumerate(invoice.invoice_line_ids, start=1):
            line_element = tag(root, "cac:InvoiceLine",
                               attrib={"id": "L%i" % index})
            tag(line_element, "cbc:InvoicedQuantity",
                "%.2f" % (line.quantity or 0.0))
            tag(line_element, "cbc:LineExtensionAmount",
                "%.2f" % (line.price_subtotal or 0.0),
                {"currencyID": currency})
        return '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(
            root, encoding="unicode")
    def _collect_issues(self):
        self.ensure_one()
        invoice = self.invoice_id
        partner = invoice.partner_id
        issues = []

        def add(code, severity, message, field_name=None):
            issues.append({
                "code": code,
                "severity": severity,
                "message": message,
                "field_name": field_name,
            })

        if not (invoice.name or "").strip():
            add("MISSING_NUMBER", "error",
                _("The invoice has no number; every e-invoice must carry "
                  "the posted invoice reference."), "name")
        if not invoice.invoice_date:
            add("MISSING_DATE", "error",
                _("The invoice date is missing."), "invoice_date")
        if not partner or not (partner.name or "").strip():
            add("MISSING_PARTNER", "error",
                _("The invoice has no customer, or the customer has no "
                  "name."), "partner_id")
        if not invoice.invoice_line_ids:
            add("NO_LINE", "error",
                _("The invoice has no detail line."), "invoice_line_ids")
        if not invoice.currency_id:
            add("MISSING_CURRENCY", "error",
                _("The currency of the invoice is not set."), "currency_id")
        if partner and (partner.vat or "").strip() \
                and not invoice.amount_tax:
            add("MISSING_TAX", "error",
                _("The customer carries a VAT number but no tax is "
                  "collected on this invoice."), "tax_ids")
        line_sum = sum(
            invoice.invoice_line_ids.mapped("price_subtotal"))
        if invoice.invoice_line_ids and abs(
                line_sum - (invoice.amount_untaxed or 0.0)) > 0.01:
            add("LINE_MISMATCH", "error",
                _("The sum of the invoice lines does not match the "
                  "untaxed amount of the invoice."), "amount_untaxed")
        if abs((invoice.amount_untaxed or 0.0) + (invoice.amount_tax or 0.0)
               - (invoice.amount_total or 0.0)) > 0.01:
            add("TOTAL_MISMATCH", "error",
                _("The untaxed amount plus the taxes does not match the "
                  "total of the invoice."), "amount_total")
        if self.xml_data:
            if invoice.name and invoice.name not in self.xml_data:
                add("XML_REF_MISMATCH", "warning",
                    _("The XML document does not contain the number of the "
                      "posted invoice."), "xml_data")
            match = re.search(PAYABLE_PATTERN, self.xml_data)
            if not match:
                add("MISSING_XML_TOTAL", "error",
                    _("The XML document does not contain a payable "
                      "amount."), "xml_data")
            else:
                try:
                    xml_total = float(match.group(1))
                except ValueError:
                    xml_total = None
                if xml_total is None or abs(
                        xml_total
                        - (invoice.amount_total or 0.0)) > 0.01:
                    add("TOTAL_MISMATCH", "error",
                        _("The payable amount of the XML document does not "
                          "match the total of the invoice."), "xml_data")
        return issues

    def action_generate(self):
        for check in self:
            invoice = check.invoice_id
            if not invoice or invoice.move_type != "out_invoice":
                raise UserError(_(
                    "An e-invoicing document can only be generated for a "
                    "customer invoice."))
            if invoice.state != "posted":
                raise UserError(_(
                    "Post the customer invoice before generating its "
                    "e-invoicing XML."))
            xml = check._build_xml(invoice)
            check._replace_issues([])
            check.write({"xml_data": xml, "state": "generated"})
            check.message_post(body=_(
                "E-invoicing XML generated in format %(format)s.",
                format=check.format))
        return True

    def action_validate(self):
        for check in self:
            if not check.xml_data:
                raise UserError(_(
                    "Generate the XML document before running the "
                    "validation."))
            issues = check._collect_issues()
            check._replace_issues(issues)
            errors = [issue for issue in issues
                      if issue["severity"] == "error"]
            if errors:
                check.write({"state": "invalid"})
                check.message_post(body=_(
                    "Validation failed: %(count)s error(s) and "
                    "%(warnings)s warning(s) found.",
                    count=len(errors),
                    warnings=len(issues) - len(errors)))
            else:
                check.write({"state": "valid"})
                check.message_post(body=_(
                    "Validation passed: no error, %(warnings)s "
                    "warning(s) recorded.", warnings=len(issues)))
        return True

    def action_reset(self):
        for check in self:
            if check.state == "draft":
                raise UserError(_(
                    "Only a generated or already validated check can be "
                    "reset to draft."))
            check._replace_issues([])
            check.write({"state": "draft", "xml_data": False})
            check.message_post(body=_(
                "Check reset to draft: the XML document and the issues "
                "have been cleared."))
        return True


class EinvoiceIssue(models.Model):
    _name = "einvoice.issue"
    _description = "E-Invoice Issue"
    _order = "severity, code, id"

    check_id = fields.Many2one(
        "einvoice.check", string="Check", required=True,
        ondelete="cascade", index=True)
    code = fields.Char(
        string="Code", required=True, index=True,
        help="Short technical code of the issue, for example MISSING_TAX.")
    severity = fields.Selection(
        [("error", "Error"), ("warning", "Warning")],
        string="Severity", required=True, default="error", index=True,
        help="An error makes the check invalid; a warning is recorded "
             "without blocking the check.")
    message = fields.Char(string="Message", required=True)
    field_name = fields.Char(
        string="Field",
        help="Technical name of the invoice field concerned by the "
             "issue.")
    company_id = fields.Many2one(
        related="check_id.company_id", string="Company",
        store=True, readonly=True)
