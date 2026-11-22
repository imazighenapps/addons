# -*- coding: utf-8 -*-
"""Générateur SAF-T (AuditFile OECD) : Header + MasterFiles + GL Entries."""
import base64
from datetime import date, datetime

from lxml import etree

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

PRODUCT_ID = "Odoo - saft_export_pack"


def _fmt_amount(value):
    """Montant SAF-T : point décimal, 2 décimales."""
    return "%.2f" % (value or 0.0)


def _fmt_date(value):
    return value.strftime("%Y-%m-%d") if value else ""


class SaftExport(models.Model):
    _name = "saft.export"
    _description = "Export SAF-T (audit fiscal)"
    _order = "create_date desc, id desc"

    name = fields.Char(
        string="Référence", default="Nouveau",
        readonly=True, copy=False)
    company_id = fields.Many2one(
        "res.company", string="Société", required=True,
        default=lambda self: self.env.company)
    country_profile_id = fields.Many2one(
        "saft.country.profile", string="Profil pays", required=True,
        domain="[('company_id', 'in', [company_id, False])]")
    date_from = fields.Date(
        string="Du", required=True,
        default=lambda self: fields.Date.from_string(
            "%d-01-01" % fields.Date.context_today(self).year))
    date_to = fields.Date(
        string="Au", required=True,
        default=lambda self: fields.Date.context_today(self))
    fiscal_year = fields.Char(
        string="Exercice", compute="_compute_fiscal_year", store=True)
    state = fields.Selection(
        [("draft", "Brouillon"), ("generated", "Généré")],
        string="Statut", default="draft")
    file_name = fields.Char(string="Nom du fichier", readonly=True)
    file_data = fields.Binary(string="Fichier SAF-T", readonly=True)
    generated_at = fields.Datetime(string="Généré le", readonly=True)
    entry_count = fields.Integer(string="Transactions", readonly=True)
    line_count = fields.Integer(string="Lignes d'écritures", readonly=True)
    account_count = fields.Integer(string="Comptes", readonly=True)
    total_debit = fields.Monetary(string="Total débit", readonly=True)
    total_credit = fields.Monetary(string="Total crédit", readonly=True)
    currency_id = fields.Many2one(
        related="company_id.currency_id", readonly=True)
    warnings = fields.Text(string="Contrôles de complétude", readonly=True)

    @api.depends("date_from")
    def _compute_fiscal_year(self):
        for export in self:
            export.fiscal_year = export.date_from and str(
                export.date_from.year) or ""

    @api.constrains("date_from", "date_to")
    def _check_dates(self):
        for export in self:
            if export.date_from and export.date_to and \
                    export.date_from > export.date_to:
                raise ValidationError(
                    _("La date « Du » doit précéder la date « Au »."))

    # ------------------------------------------------------------------
    # Contrôles de complétude
    # ------------------------------------------------------------------
    def action_check_completeness(self):
        for export in self:
            export.warnings = export._completeness_report()

    def _completeness_report(self):
        """Comptes/taxes non mappés + écritures validées trouvées."""
        self.ensure_one()
        profile = self.country_profile_id
        moves = self._moves()
        accounts = self.env["account.account"].search([
            ("company_ids", "in", [self.company_id.id])])
        lines = self.env["account.move.line"].search([
            ("move_id", "in", moves.ids)])
        used_accounts = lines.account_id
        mapped_count = 0
        unmapped = []
        for account in used_accounts:
            if profile.account_map_ids.filtered(
                    lambda m: m.account_id == account):
                mapped_count += 1
            else:
                unmapped.append(account.code or account.display_name)
        used_taxes = lines.tax_ids
        unmapped_taxes = [
            t.name for t in used_taxes
            if not profile.tax_map_ids.filtered(lambda m: m.tax_id == t)]
        parts = []
        if unmapped:
            parts.append(_("Comptes utilisés sans mapping explicite (%d) : "
                           "%s") % (len(unmapped), ", ".join(unmapped)))
        if unmapped_taxes:
            parts.append(_("Taxes utilisées sans mapping (%d) : %s")
                         % (len(unmapped_taxes), ", ".join(unmapped_taxes)))
        if profile.require_explicit_account_map and unmapped:
            parts.append(_(
                "Le profil exige un mapping explicite : %d comptes sans "
                "ligne de mapping.") % len(unmapped))
        if not parts:
            parts.append(_("Complétude OK : %d comptes mappés (explicite ou "
                           "fallback), %d taxes mappées, %d écritures "
                           "trouvées dans la période.")
                         % (len(used_accounts), len(used_taxes), len(moves)))
        return "\n".join(parts)

    def _moves(self):
        self.ensure_one()
        return self.env["account.move"].search([
            ("state", "=", "posted"),
            ("date", ">=", self.date_from),
            ("date", "<=", self.date_to),
            ("company_id", "=", self.company_id.id),
        ], order="date, id")

    # ------------------------------------------------------------------
    # Génération XML
    # ------------------------------------------------------------------
    def action_generate(self):
        for export in self:
            export._generate()

    def _generate(self):
        self.ensure_one()
        if not self.name or self.name == _("Nouveau") or self.name == "Nouveau":
            self.name = self.env["ir.sequence"].next_by_code("saft.export")
        profile = self.country_profile_id
        moves = self._moves()
        if not moves:
            raise UserError(_(
                "Aucune écriture validée dans la période sélectionnée."))
        amls = self.env["account.move.line"].search(
            [("move_id", "in", moves.ids)], order="move_id, id")

        root = etree.Element(
            "AuditFile", nsmap={None: profile.namespace or None})
        self._build_header(root, profile)
        master = etree.SubElement(root, "MasterFiles")
        account_balance = self._build_gl_accounts(master, profile, amls)
        self._build_partners(master, amls)
        self._build_tax_table(master, profile, amls)
        entries = etree.SubElement(root, "GeneralLedgerEntries")
        totals = self._build_gl_entries(entries, moves, profile)

        etree.SubElement(entries, "NumberEntries").text = str(
            totals["entry_count"])
        etree.SubElement(entries, "TotalDebit").text = _fmt_amount(
            totals["total_debit"])
        etree.SubElement(entries, "TotalCredit").text = _fmt_amount(
            totals["total_credit"])

        try:
            etree.indent(root, space="  ")
        except AttributeError:
            pass
        xml_bytes = etree.tostring(
            root, xml_declaration=True, encoding="UTF-8")

        self.write({
            "file_name": "SAFT_%s_%s_%s.xml" % (
                profile.country_code, self.date_from.strftime("%Y%m%d"),
                self.date_to.strftime("%Y%m%d")),
            "file_data": base64.b64encode(xml_bytes).decode("ascii"),
            "generated_at": fields.Datetime.now(),
            "state": "generated",
            "entry_count": totals["entry_count"],
            "line_count": totals["line_count"],
            "account_count": len(account_balance),
            "total_debit": totals["total_debit"],
            "total_credit": totals["total_credit"],
            "warnings": self._completeness_report(),
        })

    def _build_header(self, root, profile):
        company = self.company_id
        header = etree.SubElement(root, "Header")
        etree.SubElement(header, "AuditFileVersion").text = \
            profile.schema_version
        etree.SubElement(header, "AuditFileCountry").text = \
            profile.country_code
        etree.SubElement(header, "AuditFileCurrency").text = \
            company.currency_id.name
        etree.SubElement(header, "DateCreated").text = _fmt_date(
            date.today())
        etree.SubElement(header, "ProductID").text = PRODUCT_ID
        etree.SubElement(header, "ProductVersion").text = "20.0.1.0.0"
        company_node = etree.SubElement(header, "Company")
        etree.SubElement(company_node, "TaxRegistrationNumber").text = \
            _clean_vat(company.vat)
        etree.SubElement(company_node, "CompanyName").text = \
            company.name or ""
        address = etree.SubElement(company_node, "CompanyAddress")
        etree.SubElement(address, "AddressDetail").text = \
            company.street or ""
        etree.SubElement(address, "City").text = company.city or ""
        etree.SubElement(address, "PostalCode").text = company.zip or ""
        etree.SubElement(address, "Country").text = \
            (company.country_id and company.country_id.code) or ""
        etree.SubElement(company_node, "CompanyTelephone").text = \
            company.phone or ""
        etree.SubElement(company_node, "CompanyEmail").text = \
            company.email or ""
        etree.SubElement(company_node, "FiscalYear").text = self.fiscal_year
        etree.SubElement(company_node, "StartDate").text = _fmt_date(
            self.date_from)
        etree.SubElement(company_node, "EndDate").text = _fmt_date(
            self.date_to)

    def _build_gl_accounts(self, master, profile, amls):
        """Comptes utilisés dans la période, soldes d'ouverture/clôture."""
        accounts = amls.account_id.sorted(lambda a: a.code or "")
        balances = {}
        for aml in amls:
            code = aml.account_id.id
            bal = balances.setdefault(
                aml.account_id, {"debit": 0.0, "credit": 0.0})
            bal["debit"] += aml.debit or 0.0
            bal["credit"] += aml.credit or 0.0
        node = etree.SubElement(master, "GeneralLedgerAccounts")
        for account in accounts:
            bal = balances[account]
            net = bal["debit"] - bal["credit"]
            account_node = etree.SubElement(node, "Account")
            etree.SubElement(account_node, "AccountID").text = \
                account.code or str(account.id)
            etree.SubElement(account_node, "AccountDescription").text = \
                account.name or ""
            etree.SubElement(
                account_node, "OpeningDebitBalance").text = "0.00"
            etree.SubElement(
                account_node, "OpeningCreditBalance").text = "0.00"
            etree.SubElement(
                account_node, "ClosingDebitBalance").text = _fmt_amount(
                    max(net, 0.0))
            etree.SubElement(
                account_node, "ClosingCreditBalance").text = _fmt_amount(
                    max(-net, 0.0))
            account_type = profile.account_type_for(account)
            if account_type:
                etree.SubElement(
                    account_node, "AccountType").text = account_type
        return balances

    def _build_partners(self, master, amls):
        partners = amls.partner_id.filtered(
            lambda p: p.name).sorted("name")
        customers = partners.filtered(lambda p: p.customer_rank > 0)
        suppliers = partners.filtered(lambda p: p.supplier_rank > 0)
        for tag, subset in (("Customers", customers),
                            ("Suppliers", suppliers)):
            if not subset:
                continue
            node = etree.SubElement(master, tag)
            for partner in subset:
                entry = etree.SubElement(node, tag[:-1])
                etree.SubElement(
                    entry, "CustomerID" if tag == "Customers"
                    else "SupplierID").text = partner.ref or str(partner.id)
                etree.SubElement(
                    entry, "CustomerName" if tag == "Customers"
                    else "SupplierName").text = partner.name or ""
                vat = _clean_vat(partner.vat)
                if vat:
                    etree.SubElement(
                        entry, "CustomerTaxID" if tag == "Customers"
                        else "SupplierTaxID").text = vat

    def _build_tax_table(self, master, profile, amls):
        taxes = amls.tax_ids.sorted("sequence")
        if not taxes:
            return
        node = etree.SubElement(master, "TaxTable")
        for tax in taxes:
            mapping = profile.tax_map_ids.filtered(
                lambda m: m.tax_id == tax)
            entry = etree.SubElement(node, "TaxTableEntry")
            etree.SubElement(entry, "TaxType").text = \
                (mapping.saft_tax_type if mapping else "VAT")
            etree.SubElement(entry, "TaxCode").text = \
                (mapping.saft_tax_code if mapping else
                 tax.tax_group_id.name or tax.name)
            rate = mapping.saft_tax_rate if mapping else tax.amount
            etree.SubElement(entry, "TaxPercentage").text = "%.2f" % (
                rate or 0.0)

    def _build_gl_entries(self, entries, moves, profile):
        total_debit = 0.0
        total_credit = 0.0
        entry_count = 0
        line_count = 0
        for move in moves:
            lines = move.line_ids
            debit = sum(l.debit or 0.0 for l in lines)
            credit = sum(l.credit or 0.0 for l in lines)
            total_debit += debit
            total_credit += credit
            entry_count += 1
            journal = etree.SubElement(entries, "Journal")
            etree.SubElement(journal, "JournalID").text = \
                move.journal_id.code or str(move.journal_id.id)
            etree.SubElement(journal, "Description").text = \
                move.journal_id.name or ""
            transaction = etree.SubElement(journal, "Transaction")
            etree.SubElement(transaction, "TransactionID").text = \
                move.name or str(move.id)
            etree.SubElement(transaction, "Period").text = "%02d" % (
                move.date.month)
            etree.SubElement(transaction, "TransactionDate").text = \
                _fmt_date(move.date)
            etree.SubElement(transaction, "SourceID").text = \
                move.name or str(move.id)
            etree.SubElement(transaction, "Description").text = \
                move.ref or move.name or ""
            etree.SubElement(transaction, "TransactionType").text = "N"
            for aml in lines:
                line_count += 1
                line = etree.SubElement(transaction, "Line")
                etree.SubElement(line, "RecordID").text = str(aml.id)
                etree.SubElement(line, "AccountID").text = \
                    aml.account_id.code or str(aml.account_id.id)
                etree.SubElement(line, "Description").text = aml.name or ""
                etree.SubElement(line, "DebitAmount").text = _fmt_amount(
                    aml.debit)
                etree.SubElement(line, "CreditAmount").text = _fmt_amount(
                    aml.credit)
        return {
            "total_debit": total_debit,
            "total_credit": total_credit,
            "entry_count": entry_count,
            "line_count": line_count,
        }


def _clean_vat(vat):
    if not vat:
        return ""
    return "".join(ch for ch in vat if ch.isalnum()).upper()
