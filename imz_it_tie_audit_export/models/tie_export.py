# -*- coding: utf-8 -*-
"""Export d'audit TIE : CSV structuré des écritures par registre fiscal."""
import base64
import io
import csv

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

TIE_COLUMNS = [
    "RegistroFiscale", "CodiceJournal", "Data", "NumeroDocumento",
    "CodiceConto", "DescrizioneConto", "Parte", "Importo",
    "ParteId", "PartnerCodiceFiscale", "PartnerRagioneSociale", "Descrizione",
]


def _fmt_amount(value):
    return ("%.2f" % (value or 0.0)).replace(".", ",")


def _fmt_date(value):
    return value.strftime("%Y%m%d") if value else ""


def _clean_vat(vat):
    if not vat:
        return ""
    return "".join(ch for ch in vat if ch.isalnum()).upper()


class TieExport(models.Model):
    _name = "tie.export"
    _description = "Export TIE Italie (audit)"
    _inherit = ["mail.thread"]
    _order = "create_date desc, id desc"

    name = fields.Char(
        string="Référence", default="Nouveau", readonly=True, copy=False)
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
        "account.journal", string="Journaux (vide = tous)")
    allow_unmapped = fields.Boolean(
        string="Autoriser journaux non mappés",
        help="Inclut les écritures des journaux sans registre fiscal "
             "(registre NON_MAPPATO) au lieu de bloquer l'export.")
    state = fields.Selection(
        [("draft", "Brouillon"), ("generated", "Généré"),
         ("deposited", "Déposé")],
        string="Statut", default="draft")
    file_name = fields.Char(string="Nom du fichier", readonly=True)
    file_data = fields.Binary(string="Fichier TIE", readonly=True)
    record_count = fields.Integer(string="Enregistrements", readonly=True)
    total_debit = fields.Monetary(string="Total débit", readonly=True)
    total_credit = fields.Monetary(string="Total crédit", readonly=True)
    currency_id = fields.Many2one(
        related="company_id.currency_id", readonly=True)
    warnings = fields.Text(string="Contrôles de complétude", readonly=True)
    deposited_on = fields.Date(
        string="Déposé le", readonly=True, tracking=True)
    deposited_by = fields.Many2one(
        "res.users", string="Déposé par", readonly=True)

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

    def action_check_completeness(self):
        for export in self:
            export.warnings = export._completeness_report()

    def _completeness_report(self):
        self.ensure_one()
        moves = self._moves()
        if not moves:
            return _("Aucune écriture validée dans la période.")
        used_journals = moves.journal_id
        maps = self.company_id.tie_registry_map_ids
        unmapped = used_journals.filtered(
            lambda j: not maps.filtered(lambda m: j in m.journal_ids))
        if unmapped:
            return _("Journaux de la période sans registre fiscal mappé "
                     "(%d) : %s") % (
                len(unmapped), ", ".join(
                    "%s (%s)" % (j.code, j.name) for j in unmapped))
        return _("Complétude OK : %d journaux utilisés, tous mappés à un "
                 "registre fiscal (%d écritures).") % (
            len(used_journals), len(moves))

    # ------------------------------------------------------------------
    # Génération CSV
    # ------------------------------------------------------------------
    def action_generate(self):
        for export in self:
            export._generate()

    def _generate(self):
        self.ensure_one()
        if not self.name or self.name in ("Nouveau", _("Nouveau")):
            self.name = self.env["ir.sequence"].next_by_code("tie.export")
        moves = self._moves()
        if not moves:
            raise UserError(_(
                "Aucune écriture validée dans la période sélectionnée."))
        maps = self.company_id.tie_registry_map_ids
        used_journals = moves.journal_id
        unmapped = used_journals.filtered(
            lambda j: not maps.filtered(lambda m: j in m.journal_ids))
        if unmapped and not self.allow_unmapped:
            raise UserError(_(
                "Journaux sans registre fiscal mappé : %s. Configurez le "
                "mapping des registres ou activez « Autoriser journaux non "
                "mappés ».") % ", ".join(unmapped.mapped("code")))

        buf = io.StringIO()
        writer = csv.writer(buf, delimiter=";", lineterminator="\r\n")
        writer.writerow([
            "TIE", _clean_vat(self.company_id.vat),
            _fmt_date(self.date_from), _fmt_date(self.date_to), "20.0.1.0.0"])
        writer.writerow(TIE_COLUMNS)
        total_debit = 0.0
        total_credit = 0.0
        record_count = 0
        for move in moves:
            registry = maps.journal_for(move.journal_id) or "NON_MAPPATO"
            for aml in move.line_ids:
                partner = aml.partner_id
                parte = "D" if (aml.debit or 0.0) >= (aml.credit or 0.0) else "A"
                writer.writerow([
                    registry, move.journal_id.code or "",
                    _fmt_date(move.date), move.name or "",
                    aml.account_id.code or "", aml.account_id.name or "",
                    parte, _fmt_amount(aml.debit or aml.credit),
                    str(aml.id),
                    _clean_vat(partner.vat) if partner else "",
                    partner.name or "" if partner else "",
                    aml.name or "",
                ])
                total_debit += aml.debit or 0.0
                total_credit += aml.credit or 0.0
                record_count += 1
        writer.writerow(["TOT", str(record_count),
                         _fmt_amount(total_debit), _fmt_amount(total_credit)])
        xml_bytes = buf.getvalue().encode("utf-8-sig")

        self.write({
            "file_name": "TIE_%s_%s_%s.csv" % (
                _clean_vat(self.company_id.vat) or "NOVAT",
                _fmt_date(self.date_from), _fmt_date(self.date_to)),
            "file_data": base64.b64encode(xml_bytes).decode("ascii"),
            "record_count": record_count,
            "total_debit": total_debit,
            "total_credit": total_credit,
            "state": "generated",
            "warnings": self._completeness_report(),
        })
    def action_mark_deposited(self):
        """Trace le dépôt effectif du fichier à l'administration."""
        self.ensure_one()
        if self.state != "generated":
            raise UserError(_(
                "Générez d'abord le fichier TIE avant de tracer le dépôt."))
        self.write({
            "state": "deposited",
            "deposited_on": fields.Date.context_today(self),
            "deposited_by": self.env.user.id,
        })

    def action_reset(self):
        self.write({
            "state": "draft", "file_data": False, "file_name": False,
            "record_count": 0, "total_debit": 0.0, "total_credit": 0.0,
            "deposited_on": False, "deposited_by": False})
