# -*- coding: utf-8 -*-
import datetime
import xml.etree.ElementTree as ElementTree

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

DATE_FORMATS = ("%Y-%m-%d", "%d/%m/%Y", "%d.%m.%Y", "%d-%m-%Y")


def _parse_statement_date(text):
    """Return a date object from the textual date of a statement row."""
    text = (text or "").strip()
    if not text:
        raise ValueError(_("A statement row has no date."))
    for fmt in DATE_FORMATS:
        try:
            return datetime.datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    try:
        return fields.Date.to_date(text)
    except ValueError:
        pass
    raise ValueError(_("Unrecognized statement date: %s.", text))


def _parse_amount(text):
    """Parse the amount of a statement row, keeping its sign."""
    raw = (text or "").replace(" ", "").replace("\u00a0", "").strip()
    if not raw:
        raise ValueError(_("A statement row has no amount."))
    try:
        return float(raw.replace(",", "."))
    except ValueError:
        raise ValueError(_("Invalid statement amount: %s.", raw))


def _parse_camt_text(text):
    """Parse a minimal CAMT-style XML statement into entry dictionaries."""
    try:
        root = ElementTree.fromstring(text)
    except ElementTree.ParseError as error:
        raise ValueError(_("The file is not valid XML: %s.", error))
    entries = []
    for entry in root.findall(".//entry"):
        date_text = (entry.findtext("date") or "").strip()
        amount_text = (entry.findtext("amount") or "").strip()
        indicator = (entry.findtext("credit-debit-indicator")
                     or "CRDT").strip().upper()
        label = (entry.findtext("nav-info")
                 or entry.findtext("name") or "").strip()
        reference = (entry.findtext("ref") or "").strip()
        if not date_text or not amount_text:
            raise ValueError(_(
                "A CAMT entry is missing its date or its amount."))
        amount = abs(_parse_amount(amount_text))
        if indicator == "DBIT":
            amount = -amount
        entries.append({
            "date": _parse_statement_date(date_text),
            "label": label,
            "reference": reference,
            "amount": amount,
        })
    if not entries:
        raise ValueError(_("No entry was found in the CAMT file."))
    return entries


class BankImportBatch(models.Model):
    _name = "bank.import.batch"
    _description = "Bank Import Batch"
    _inherit = ["mail.thread"]
    _order = "date desc, id desc"

    name = fields.Char(required=True, tracking=True)
    file_name = fields.Char(string="File Name")
    file_type = fields.Selection(
        [("camt", "CAMT (XML)"), ("ofx", "OFX"), ("csv", "CSV")],
        default="csv", required=True, tracking=True,
        help="The parser is chosen from the content: text is read as CSV "
             "and content starting with a tag as CAMT.")
    raw_data = fields.Text(string="Raw Content", copy=False)
    journal_id = fields.Many2one(
        "account.journal", string="Bank Journal",
        domain=[("type", "in", ("bank", "cash"))],
        help="Bank journal of the statement used for the counterpart "
             "entries.")
    date = fields.Date(
        string="Statement Date", default=fields.Date.context_today,
        tracking=True)
    currency_id = fields.Many2one(
        "res.currency", string="Currency", required=True,
        default=lambda self: self.env.company.currency_id)
    state = fields.Selection(
        [("draft", "Draft"), ("imported", "Imported"), ("error", "Error")],
        default="draft", required=True, copy=False, tracking=True,
        index=True)
    line_ids = fields.One2many(
        "bank.import.line", "batch_id", string="Transactions", copy=True)
    total_amount = fields.Monetary(
        string="Total Amount", currency_field="currency_id",
        compute="_compute_total_amount", store=True,
        help="Sum of the signed amounts of every transaction of the "
             "batch.")
    error_message = fields.Text(
        string="Error Message", copy=False, readonly=True)
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True)

    _name_company_uniq = models.Constraint(
        "UNIQUE(name, company_id)",
        "The batch name must be unique per company.")

    @api.depends("line_ids.amount")
    def _compute_total_amount(self):
        for batch in self:
            batch.total_amount = sum(batch.line_ids.mapped("amount"))

    @api.constrains("date")
    def _check_date(self):
        for batch in self:
            if batch.date and batch.date > fields.Date.context_today(batch):
                raise ValidationError(_(
                    "The statement date of the batch \"%s\" cannot be in "
                    "the future.", batch.name))

    def _parse_raw_data(self):
        """Return a list of transaction dictionaries from the raw content."""
        self.ensure_one()
        text = (self.raw_data or "").strip()
        if not text:
            raise ValueError(_("The batch has no raw content to parse."))
        if text.startswith("<"):
            return _parse_camt_text(text)
        return self._parse_csv_text()

    def _parse_csv_text(self):
        """Parse "date;label;reference;amount" rows, header optional."""
        self.ensure_one()
        entries = []
        first_row = True
        for raw_line in (self.raw_data or "").splitlines():
            row = raw_line.strip()
            if not row:
                continue
            parts = [part.strip() for part in row.split(";")]
            if len(parts) != 4:
                raise ValueError(_(
                    "Expected 4 columns separated by ';' "
                    "(date;label;reference;amount) but found %s in \"%s\".",
                    len(parts), row))
            date_text, label, reference, amount_text = parts
            if first_row:
                first_row = False
                try:
                    _parse_statement_date(date_text)
                except ValueError:
                    continue  # optional header row
            entries.append({
                "date": _parse_statement_date(date_text),
                "label": label,
                "reference": reference,
                "amount": _parse_amount(amount_text),
            })
        return entries

    def action_parse(self):
        for batch in self:
            if batch.state == "imported":
                raise UserError(_(
                    "The batch \"%s\" has already been imported. Create a "
                    "new batch to import the file again.", batch.name))
            batch.line_ids.unlink()
            try:
                entries = batch._parse_raw_data()
                if not entries:
                    raise ValueError(_(
                        "No transaction was found in the file."))
            except Exception as error:
                batch.write({
                    "state": "error",
                    "error_message": _("Parsing failed: %s", error),
                })
                batch.message_post(body=batch.error_message)
                continue
            batch.env["bank.import.line"].create([{
                "batch_id": batch.id,
                "date": entry["date"],
                "label": entry["label"],
                "reference": entry["reference"],
                "amount": entry["amount"],
            } for entry in entries])
            batch.write({"state": "imported", "error_message": False})
            batch.message_post(body=_(
                "Parsed %s transaction(s) from %s: total %s.",
                len(entries), batch.file_name or batch.file_type,
                batch.total_amount))
        return True

    def action_apply_rules(self):
        rules = self.env["bank.import.rule"].search(
            [("active", "=", True)], order="sequence, id")
        for batch in self:
            assigned = 0
            for line in batch.line_ids:
                if line.matched:
                    continue  # a marked line keeps its match (idempotent)
                label = (line.label or "").lower()
                for rule in rules:
                    if rule.pattern.lower() not in label:
                        continue
                    vals = {"matched": True}
                    if rule.partner_id:
                        vals["partner_id"] = rule.partner_id.id
                    if rule.account_id:
                        vals["account_id"] = rule.account_id.id
                    line.write(vals)
                    assigned += 1
                    break
            if not rules:
                batch.message_post(body=_(
                    "No active import rule: nothing could be matched."))
            else:
                batch.message_post(body=_(
                    "%s transaction(s) matched by the import rules.",
                    assigned))
        return True

    def action_flag_duplicates(self):
        for batch in self:
            batch.modified(["state"])
        self.env.flush_all()
        for batch in self:
            flagged = len(batch.line_ids.filtered("duplicate"))
            batch.message_post(body=_(
                "Duplicate check: %s transaction(s) share a date, an "
                "amount and a label with a transaction already imported.",
                flagged))
        return True


class BankImportLine(models.Model):
    _name = "bank.import.line"
    _description = "Bank Import Transaction"
    _order = "batch_id, date, id"

    batch_id = fields.Many2one(
        "bank.import.batch", string="Batch", required=True,
        ondelete="cascade", index=True)
    date = fields.Date(required=True)
    label = fields.Char(string="Label")
    reference = fields.Char()
    amount = fields.Monetary(required=True, currency_field="currency_id")
    currency_id = fields.Many2one(
        related="batch_id.currency_id", store=True, readonly=True)
    partner_id = fields.Many2one("res.partner", string="Partner")
    account_id = fields.Many2one("account.account", string="Account")
    matched = fields.Boolean(
        string="Rule Matched", default=False, copy=False,
        help="The line was matched by an import rule.")
    duplicate = fields.Boolean(
        string="Duplicate", compute="_compute_duplicate", store=True,
        copy=False,
        help="The line has the same date, amount and label as a "
             "transaction already imported.")
    company_id = fields.Many2one(
        related="batch_id.company_id", store=True, readonly=True)

    def _has_prior_duplicate(self):
        self.ensure_one()
        if not self.date or not self.label:
            return False
        domain = [
            ("company_id", "=", self.company_id.id),
            ("date", "=", self.date),
            ("amount", "=", self.amount),
            ("label", "=", self.label),
            ("batch_id.state", "=", "imported"),
        ]
        if self.batch_id.state == "imported":
            domain.append(("id", "!=", self.id))
        else:
            domain.append(("batch_id", "!=", self.batch_id.id))
        return bool(self.search(domain, limit=1))

    @api.depends("batch_id.state", "date", "amount", "label", "company_id")
    def _compute_duplicate(self):
        for line in self:
            line.duplicate = line._has_prior_duplicate()


class BankImportRule(models.Model):
    _name = "bank.import.rule"
    _description = "Bank Import Rule"
    _order = "sequence, id"

    name = fields.Char(required=True)
    pattern = fields.Char(
        required=True,
        help="Text looked for inside the transaction label, case "
             "insensitive.")
    partner_id = fields.Many2one("res.partner", string="Partner")
    account_id = fields.Many2one(
        "account.account", string="Account",
        help="Account assigned to the matched transactions.")
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)

    _pattern_not_empty = models.Constraint(
        "CHECK(pattern <> '')",
        "The rule pattern cannot be empty.")

    @api.constrains("pattern")
    def _check_pattern(self):
        for rule in self:
            if not (rule.pattern or "").strip():
                raise ValidationError(_(
                    "The pattern of the rule \"%s\" cannot be blank.",
                    rule.name))
