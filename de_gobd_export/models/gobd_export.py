# -*- coding: utf-8 -*-
"""Export GoBD (GDPdU) : index XML + écritures comptables, archive ZIP."""
import base64
import csv
import io
import zipfile
from datetime import date

from lxml import etree

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

GDPDU_NS = "urn:schemas-microsoft-com:xml-analysis:rowset"


def _fmt_date(value):
    return value.strftime("%Y-%m-%d") if value else ""


def _fmt_amount(value):
    return ("%.2f" % (value or 0.0)).replace(".", ",")


class GobdExport(models.Model):
    _name = "gobd.export"
    _description = "Export GoBD Allemagne (GDPdU)"
    _inherit = ["mail.thread"]
    _order = "create_date desc, id desc"

    name = fields.Char(
        string="Référence", default="Nouveau", readonly=True, copy=False)
    company_id = fields.Many2one(
        "res.company", string="Société", required=True,
        default=lambda self: self.env.company)
    date_from = fields.Date(string="Du", required=True)
    date_to = fields.Date(string="Au", required=True)
    journal_ids = fields.Many2many(
        "account.journal", string="Journaux",
        help="Aucun journal sélectionné : tous les journaux de la société.")
    state = fields.Selection(
        [("draft", "Brouillon"), ("generated", "Généré")],
        string="Statut", default="draft", tracking=True)
    file_name = fields.Char(string="Nom du fichier", readonly=True)
    file_data = fields.Binary(string="Archive GoBD", readonly=True)
    generated_at = fields.Datetime(string="Généré le", readonly=True)
    entry_count = fields.Integer(string="Écritures", readonly=True)
    line_count = fields.Integer(string="Lignes", readonly=True)
    total_debit = fields.Monetary(string="Total débit", readonly=True)
    total_credit = fields.Monetary(string="Total crédit", readonly=True)
    currency_id = fields.Many2one(
        related="company_id.currency_id", readonly=True)
    protocol_note = fields.Text(string="Protocole de remise", readonly=True)

    @api.constrains("date_from", "date_to")
    def _check_dates(self):
        for rec in self:
            if rec.date_from and rec.date_to and rec.date_from > rec.date_to:
                raise ValidationError(
                    _("La date « Du » doit précéder la date « Au »."))

    def _moves(self):
        self.ensure_one()
        domain = [
            ("state", "=", "posted"),
            ("date", ">=", self.date_from),
            ("date", "<=", self.date_to),
            ("company_id", "=", self.company_id.id),
        ]
        if self.journal_ids:
            domain.append(("journal_id", "in", self.journal_ids.ids))
        return self.env["account.move"].search(domain, order="date, id")

    def action_generate(self):
        for rec in self:
            rec._generate()

    def _generate(self):
        self.ensure_one()
        if not self.name or self.name in ("Nouveau", _("Nouveau")):
            self.name = self.env["ir.sequence"].next_by_code("gobd.export") or "GOBD"
        moves = self._moves()
        if not moves:
            raise UserError(_(
                "Aucune écriture validée dans la période sélectionnée."))
        amls = self.env["account.move.line"].search(
            [("move_id", "in", moves.ids)], order="move_id, id")

        data_csv = self._build_data_csv(amls)
        index_xml = self._build_index_xml(len(amls))
        zip_bytes = self._build_zip(index_xml, data_csv)

        total_debit = sum(l.debit or 0.0 for l in amls)
        total_credit = sum(l.credit or 0.0 for l in amls)
        fname = "GoBD_%s_%s_%s.zip" % (
            (self.company_id.name or "COMP").replace(" ", "_")[:20],
            self.date_from.strftime("%Y%m%d"),
            self.date_to.strftime("%Y%m%d"))
        protocol = _(
            "Protocole de remise GoBD\n"
            "Référence : %s\nSociété : %s\nPériode : %s au %s\n"
            "Écritures : %d | Lignes : %d\n"
            "Total débit : %.2f | Total crédit : %.2f\n"
            "Généré le : %s\nFichiers : index.xml, journal_entries.csv"
        ) % (self.name, self.company_id.display_name,
             self.date_from, self.date_to, len(moves), len(amls),
             total_debit, total_credit,
             fields.Datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        self.write({
            "file_name": fname,
            "file_data": base64.b64encode(zip_bytes).decode("ascii"),
            "generated_at": fields.Datetime.now(),
            "state": "generated",
            "entry_count": len(moves),
            "line_count": len(amls),
            "total_debit": total_debit,
            "total_credit": total_credit,
            "protocol_note": protocol,
        })

    def _build_data_csv(self, amls):
        buf = io.StringIO()
        writer = csv.writer(buf, delimiter=";", lineterminator="\r\n")
        writer.writerow([
            "MoveName", "MoveDate", "JournalCode", "AccountCode",
            "AccountName", "Partner", "Label", "Debit", "Credit",
            "Currency", "AmountCurrency",
        ])
        for aml in amls:
            writer.writerow([
                aml.move_id.name or "",
                _fmt_date(aml.date),
                aml.move_id.journal_id.code or "",
                aml.account_id.code or "",
                aml.account_id.name or "",
                aml.partner_id.display_name or "",
                aml.name or "",
                _fmt_amount(aml.debit),
                _fmt_amount(aml.credit),
                (aml.currency_id and aml.currency_id.name) or "",
                _fmt_amount(aml.amount_currency) if aml.amount_currency else "",
            ])
        return buf.getvalue().encode("utf-8-sig")

    def _build_index_xml(self, record_count):
        root = etree.Element("DataSet")
        version = etree.SubElement(root, "Version")
        version.text = "1.0"
        media = etree.SubElement(root, "Media")
        name = etree.SubElement(media, "Name")
        name.text = "GoBD_Export"
        table = etree.SubElement(media, "Table")
        url = etree.SubElement(table, "URL")
        url.text = "journal_entries.csv"
        etree.SubElement(table, "Name").text = "JournalEntries"
        etree.SubElement(table, "Description").text = _(
            "Écritures comptables exportées (GoBD)")
        etree.SubElement(table, "UTF8").text = "1"
        etree.SubElement(table, "DecimalSymbol").text = ","
        etree.SubElement(table, "DigitGroupingSymbol").text = ""
        etree.SubElement(table, "SkipNumLines").text = "1"
        etree.SubElement(table, "Range").text = "A1:K%d" % (record_count + 1)

        var = etree.SubElement(table, "VariableLength")
        cols = [
            ("MoveName", "AlphaNumeric"), ("MoveDate", "AlphaNumeric"),
            ("JournalCode", "AlphaNumeric"), ("AccountCode", "AlphaNumeric"),
            ("AccountName", "AlphaNumeric"), ("Partner", "AlphaNumeric"),
            ("Label", "AlphaNumeric"), ("Debit", "Numeric"),
            ("Credit", "Numeric"), ("Currency", "AlphaNumeric"),
            ("AmountCurrency", "Numeric"),
        ]
        colspec = etree.SubElement(var, "ColumnDelimiter")
        colspec.text = ";"
        record_delim = etree.SubElement(var, "RecordDelimiter")
        record_delim.text = "&#13;&#10;"
        text_encap = etree.SubElement(var, "TextEncapsulator")
        text_encap.text = '"'
        for cname, ctype in cols:
            vf = etree.SubElement(var, "VariableColumn")
            etree.SubElement(vf, "Name").text = cname
            etree.SubElement(vf, "Description").text = cname
            if ctype == "Numeric":
                num = etree.SubElement(vf, "Numeric")
                etree.SubElement(num, "Accuracy").text = "2"
            else:
                etree.SubElement(vf, "AlphaNumeric")

        try:
            etree.indent(root, space="  ")
        except AttributeError:
            pass
        return etree.tostring(
            root, xml_declaration=True, encoding="UTF-8")

    def _build_zip(self, index_xml, data_csv):
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("index.xml", index_xml)
            zf.writestr("journal_entries.csv", data_csv)
        return buf.getvalue()
