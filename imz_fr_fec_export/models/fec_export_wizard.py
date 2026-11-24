# -*- coding: utf-8 -*-
"""Générateur FEC (Fichier des Écritures Comptables) — article A47 A-1 du LPF.

Format BOI-FECPAT : 18 champs obligatoires + 3 champs de devise optionnels,
séparés par une tabulation ou un pipe, une ligne d'en-tête + une ligne par
écriture (par ligne de pièce comptable), montants à la virgule.
"""
import base64

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

FEC_HEADER = [
    "CodeJournal", "JournalLib", "EcritureNum", "EcritureDate",
    "CompNumMvt", "CompPieceNum", "AccountNum", "AccountLib",
    "CompAuxNum", "CompAuxLib", "PieceRef", "PieceDate", "EcritureLib",
    "Debit", "Credit", "EcritureLet", "DateLet", "ValidDate",
]
FEC_CURRENCY_HEADER = ["Monteuro", "Montantdevise", "Idevise"]

# Longueurs réglementaires (caractères) des champs texte
FEC_LIMITS = {
    "JournalLib": 38,
    "AccountNum": 11,
    "AccountLib": 76,
    "CompAuxNum": 32,
    "CompAuxLib": 76,
    "PieceRef": 12,
    "EcritureLib": 45,
    "EcritureLet": 4,
}


def _fmt_amount(value):
    """Montant FEC : séparateur décimal virgule, 2 décimales."""
    return ("%.2f" % (value or 0.0)).replace(".", ",")


def _clean(value):
    """Nettoie un libellé : retours à la ligne et tabulations supprimés."""
    if not value:
        return ""
    return " ".join(str(value).split())


class FecExportWizard(models.TransientModel):
    _name = "fec.export.wizard"
    _description = "Générateur FEC France"

    company_id = fields.Many2one(
        "res.company", string="Société", required=True,
        default=lambda self: self.env.company)
    date_from = fields.Date(
        string="Du", required=True,
        default=lambda self: fields.Date.from_string(
            "%d-01-01" % fields.Date.context_today(self).year))
    date_to = fields.Date(
        string="Au", required=True,
        default=lambda self: fields.Date.context_today(self))
    journal_ids = fields.Many2many(
        "account.journal", string="Journaux",
        help="Aucun journal sélectionné : tous les journaux de la société.")
    encoding = fields.Selection(
        [("cp1252", "ANSI (cp1252)"), ("utf-8", "UTF-8")],
        string="Encodage", required=True, default="cp1252")
    separator = fields.Selection(
        [("tab", "Tabulation"), ("pipe", "Barre verticale (|)")],
        string="Séparateur", required=True, default="tab")
    include_auxiliary = fields.Boolean(
        string="Auxiliaire partenaires", default=True,
        help="Renseigne CompAuxNum/CompAuxLib pour les écritures de tiers.")
    include_currency_cols = fields.Boolean(
        string="Colonnes de devise", default=False,
        help="Ajoute Monteuro, Montantdevise et Idevise (21 colonnes).")

    file_name = fields.Char(string="Nom du fichier", readonly=True)
    file_data = fields.Binary(string="Fichier FEC", readonly=True)
    record_count = fields.Integer(string="Enregistrements", readonly=True)
    move_count = fields.Integer(string="Écritures", readonly=True)
    total_debit = fields.Monetary(string="Total débit", readonly=True)
    total_credit = fields.Monetary(string="Total crédit", readonly=True)
    currency_id = fields.Many2one(
        related="company_id.currency_id", readonly=True)

    @api.constrains("date_from", "date_to")
    def _check_dates(self):
        for wizard in self:
            if wizard.date_from and wizard.date_to and \
                    wizard.date_from > wizard.date_to:
                raise ValidationError(
                    _("La date « Du » doit précéder la date « Au »."))

    # ------------------------------------------------------------------
    # Formatage FEC
    # ------------------------------------------------------------------
    def _siren(self):
        """SIREN à 9 chiffres extrait du numéro de TVA de la société."""
        vat = _clean(self.company_id.vat).upper()
        digits = "".join(ch for ch in vat if ch.isdigit())
        if not digits:
            raise UserError(_(
                "Le numéro de TVA (SIREN) de la société « %s » doit être "
                "renseigné pour nommer le fichier FEC.")
                % self.company_id.display_name)
        if vat.startswith("FR") and len(digits) >= 11:
            return digits[-9:]
        return digits[:9] if len(digits) >= 9 else digits

    def _format_date(self, value):
        if not value:
            return ""
        return value.strftime("%Y%m%d")

    def _fmt_field(self, key, value):
        text = _clean(value)
        limit = FEC_LIMITS.get(key)
        if limit:
            text = text[:limit]
        return text

    def _settlement_dates(self, amls):
        """Date de lettrage (max create_date des lettrages) par numéro."""
        numbers = {l.matching_number for l in amls if l.matching_number}
        if not numbers:
            return {}
        rows = self.env["account.partial.reconcile"]._read_group(
            [("matching_number", "in", sorted(numbers))],
            groupby=["matching_number"], aggregates=["create_date:max"])
        return {
            num: (dt.date() if dt else None) for num, dt in rows}

    def _lines_for_move(self, move, entry_num, settle_dates):
        """Lignes FEC d'une pièce comptable."""
        company = move.company_id
        company_cur = company.currency_id
        lines = []
        for aml in move.line_ids:
            account = aml.account_id
            partner = aml.partner_id
            is_receivable_payable = account.account_type in (
                "asset_receivable", "liability_payable")
            debit = aml.debit or 0.0
            credit = aml.credit or 0.0
            matching = aml.matching_number or ""
            row = [
                self._fmt_field("CodeJournal", move.journal_id.code),
                self._fmt_field("JournalLib", move.journal_id.name),
                str(entry_num),
                self._format_date(move.date),
                str(entry_num),
                self._fmt_field("PieceRef", move.name),
                self._fmt_field("AccountNum", account.code),
                self._fmt_field("AccountLib", account.name),
                "",
                "",
                self._fmt_field("PieceRef", move.ref or move.name),
                self._format_date(move.invoice_date or move.date),
                self._fmt_field("EcritureLib", aml.name),
                _fmt_amount(debit),
                _fmt_amount(credit),
                self._fmt_field("EcritureLet", matching),
                self._format_date(settle_dates.get(matching))
                if matching else "",
                self._format_date(move.date),
            ]
            if self.include_auxiliary and partner and is_receivable_payable:
                row[8] = self._fmt_field(
                    "CompAuxNum", partner.ref or "P%s" % partner.id)
                row[9] = self._fmt_field("CompAuxLib", partner.display_name)
            if self.include_currency_cols:
                amount_eur = debit if debit else credit
                foreign = (aml.currency_id and
                           aml.currency_id != company_cur and
                           aml.amount_currency)
                row.append(_fmt_amount(amount_eur))
                row.append(
                    _fmt_amount(abs(aml.amount_currency)) if foreign else "")
                row.append(aml.currency_id.name if foreign else "")
            lines.append(row)
        return lines

    # ------------------------------------------------------------------
    # Action principale
    # ------------------------------------------------------------------
    def action_generate(self):
        self.ensure_one()
        Move = self.env["account.move"]
        domain = [
            ("state", "=", "posted"),
            ("date", ">=", self.date_from),
            ("date", "<=", self.date_to),
            ("company_id", "=", self.company_id.id),
        ]
        if self.journal_ids:
            domain.append(("journal_id", "in", self.journal_ids.ids))
        moves = Move.search(domain, order="date, id")
        if not moves:
            raise UserError(_(
                "Aucune écriture validée dans la période sélectionnée."))

        sep = "\t" if self.separator == "tab" else "|"
        settle_dates = self._settlement_dates(
            self.env["account.move.line"].search(
                [("move_id", "in", moves.ids)]))
        counter = {}
        total_debit = 0.0
        total_credit = 0.0
        record_count = 0
        data_lines = []
        for move in moves:
            code = move.journal_id.code or "?"
            counter[code] = counter.get(code, 0) + 1
            lines = self._lines_for_move(move, counter[code], settle_dates)
            for row in lines:
                row = [c.replace(sep, " ") if sep != "\t"
                       else c.replace("\t", " ") for c in row]
                data_lines.append(sep.join(row))
                total_debit += float(row[13].replace(",", "."))
                total_credit += float(row[14].replace(",", "."))
                record_count += 1

        header = list(FEC_HEADER)
        if self.include_currency_cols:
            header += FEC_CURRENCY_HEADER
        content = sep.join(header) + "\r\n" + "\r\n".join(data_lines) + "\r\n"
        raw = content.encode(self.encoding, errors="replace")

        self.write({
            "file_name": "%sFEC%s" % (
                self._siren(), self.date_to.strftime("%Y%m%d")),
            "file_data": base64.b64encode(raw).decode("ascii"),
            "record_count": record_count,
            "move_count": len(moves),
            "total_debit": total_debit,
            "total_credit": total_credit,
        })
        return {
            "type": "ir.actions.act_window",
            "res_model": self._name,
            "res_id": self.id,
            "view_mode": "form",
            "target": "new",
        }

    def action_download(self):
        self.ensure_one()
        if not self.file_data:
            raise UserError(_("Générez d'abord le fichier FEC."))
        return {
            "type": "ir.actions.act_url",
            "url": "/web/content/?model=%s&id=%s&field=file_data&"
                   "filename_field=file_name&download=true" % (
                       self._name, self.id),
            "target": "self",
        }
