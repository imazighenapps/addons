# -*- coding: utf-8 -*-
"""Validateur FEC : analyse d'un fichier FEC et rapport d'anomalies."""
import base64
from datetime import date

from odoo import _, api, fields, models

FEC_FIELDS = [
    "CodeJournal", "JournalLib", "EcritureNum", "EcritureDate",
    "CompNumMvt", "CompPieceNum", "AccountNum", "AccountLib",
    "CompAuxNum", "CompAuxLib", "PieceRef", "PieceDate", "EcritureLib",
    "Debit", "Credit", "EcritureLet", "DateLet", "ValidDate",
]
FEC_LENGTHS = {
    "CodeJournal": 4, "JournalLib": 38, "AccountNum": 11, "AccountLib": 76,
    "CompAuxNum": 32, "CompAuxLib": 76, "PieceRef": 12, "EcritureLib": 45,
    "EcritureLet": 4,
}
DATE_FIELDS = ("EcritureDate", "PieceDate", "DateLet", "ValidDate")
MONEY_FIELDS = ("Debit", "Credit")


def _valid_date(text):
    """AAAAMMJJ calendaire valide ?"""
    if len(text) != 8 or not text.isdigit():
        return False
    try:
        date(int(text[:4]), int(text[4:6]), int(text[6:]))
        return True
    except ValueError:
        return False


def _parse_amount(text):
    """Montant FEC « 1234,56 » -> float (None si invalide)."""
    if not text:
        return 0.0
    try:
        return float(text.replace(",", ".").replace(" ", ""))
    except ValueError:
        return None


class FecValidation(models.Model):
    _name = "fec.validation"
    _description = "Validation FEC"
    _order = "create_date desc, id desc"
    _inherit = ["mail.thread"]

    name = fields.Char(string="Nom", required=True, default="Nouveau contrôle")
    company_id = fields.Many2one(
        "res.company", string="Société", required=True,
        default=lambda self: self.env.company)
    file_name = fields.Char(string="Nom du fichier")
    source_file = fields.Binary(
        string="Fichier FEC", required=True)
    state = fields.Selection(
        [("draft", "À analyser"), ("validated", "Conforme"),
         ("with_errors", "Anomalies")],
        string="Résultat", default="draft", tracking=True)
    detected_separator = fields.Char(
        string="Séparateur détecté", readonly=True)
    record_count = fields.Integer(string="Enregistrements", readonly=True)
    total_debit = fields.Monetary(string="Total débit", readonly=True)
    total_credit = fields.Monetary(string="Total crédit", readonly=True)
    balance_gap = fields.Monetary(string="Écart de balance", readonly=True)
    error_count = fields.Integer(
        string="Erreurs", compute="_compute_counts", store=True)
    warning_count = fields.Integer(
        string="Avertissements", compute="_compute_counts", store=True)
    currency_id = fields.Many2one(
        related="company_id.currency_id", readonly=True)
    line_ids = fields.One2many(
        "fec.validation.error", "validation_id", string="Anomalies")

    @api.depends("line_ids", "line_ids.severity")
    def _compute_counts(self):
        for validation in self:
            validation.error_count = len(
                validation.line_ids.filtered(
                    lambda l: l.severity == "error"))
            validation.warning_count = len(
                validation.line_ids.filtered(
                    lambda l: l.severity == "warning"))

    def action_reset(self):
        self.line_ids.unlink()
        self.state = "draft"

    # ------------------------------------------------------------------
    # Analyse
    # ------------------------------------------------------------------
    def action_validate(self):
        for validation in self:
            validation.line_ids.unlink()
            errors = validation._analyze()
            for error in errors:
                self.env["fec.validation.error"].create(error)
            validation.state = ("validated"
                                if validation.error_count == 0
                                else "with_errors")

    def _decode_file(self):
        """Décode le fichier en texte (utf-8 puis cp1252)."""
        self.ensure_one()
        raw = base64.b64decode(self.source_file or b"")
        for encoding in ("utf-8-sig", "cp1252"):
            try:
                return raw.decode(encoding)
            except UnicodeDecodeError:
                continue
        return raw.decode("latin-1", errors="replace")

    def _analyze(self):
        """Retourne une liste d'anomalies (dicts pour create())."""
        self.ensure_one()
        text = self._decode_file()
        rows = [r for r in text.splitlines() if r.strip()]
        if not rows:
            return [self._error(0, "", "missing", "error",
                                _("Le fichier est vide."))]
        header = rows[0]
        errors = []
        # Séparateur : celui qui structure la ligne d'en-tête
        for sep_char, label in (("\t", "tabulation"), ("|", "pipe"),
                                (";", "point-virgule")):
            if sep_char in header:
                sep = sep_char
                self.detected_separator = label
                break
        else:
            return [self._error(1, "", "format", "error",
                                _("Aucun séparateur reconnu (tabulation, "
                                  "pipe ou point-virgule) dans l'en-tête."))]

        cols = [c.strip() for c in header.split(sep)]
        # Contrôles d'en-tête
        missing = [f for f in FEC_FIELDS if f not in cols]
        if len(cols) < 18:
            errors.append(self._error(
                1, "", "format", "error",
                _("L'en-tête n'a que %d colonnes (18 obligatoires).")
                % len(cols)))
        if missing:
            errors.append(self._error(
                1, ", ".join(missing), "missing", "error",
                _("Champs obligatoires absents de l'en-tête : %s.")
                % ", ".join(missing)))
        if cols[:18] != FEC_FIELDS and not missing:
            errors.append(self._error(
                1, "", "format", "warning",
                _("Les 18 champs ne sont pas dans l'ordre réglementaire.")))

        idx = {f: (cols.index(f) if f in cols else -1) for f in FEC_FIELDS}
        idx["CompAuxNum"] = cols.index("CompAuxNum") if "CompAuxNum" in cols else -1
        idx["CompAuxLib"] = cols.index("CompAuxLib") if "CompAuxLib" in cols else -1
        extra_names = [c for c in cols if c not in FEC_FIELDS +
                       ["CompAuxNum", "CompAuxLib"]]
        if extra_names:
            errors.append(self._error(
                1, ", ".join(extra_names), "format", "warning",
                _("Colonnes non réglementaires : %s.") % ", ".join(extra_names)))

        pieces_by_line = {}
        total_debit = 0.0
        total_credit = 0.0
        record_count = 0
        seen_keys = set()
        piece_movement = {}
        last_num = {}
        for pos, row in enumerate(rows[1:], start=2):
            values = [c.strip() for c in row.split(sep)]
            if len(values) != len(cols):
                errors.append(self._error(
                    pos, "", "format", "error",
                    _("La ligne a %d colonnes (attendu %d).")
                    % (len(values), len(cols))))
                continue
            record_count += 1
            row_map = {f: (values[i] if i >= 0 else "") for f, i in idx.items()}
            pieces_by_line[pos] = row_map["CompPieceNum"]

            # Champs obligatoires présents
            for field_name in ("CodeJournal", "JournalLib", "EcritureNum",
                               "EcritureDate", "CompNumMvt", "CompPieceNum",
                               "AccountNum", "AccountLib", "PieceRef",
                               "EcritureLib", "ValidDate"):
                if not row_map[field_name]:
                    errors.append(self._error(
                        pos, field_name, "missing", "error",
                        _("%s manquant (ligne %d).") % (field_name, pos)))

            # Longueurs réglementaires
            for field_name, limit in FEC_LENGTHS.items():
                if idx[field_name] >= 0 and len(row_map[field_name]) > limit:
                    errors.append(self._error(
                        pos, field_name, "length", "error",
                        _("%s trop long (%d caractères, max %d).")
                        % (field_name, len(row_map[field_name]), limit)))

            # Numériques
            entry_num = row_map["EcritureNum"]
            if entry_num and not entry_num.isdigit():
                errors.append(self._error(
                    pos, "EcritureNum", "format", "error",
                    _("EcritureNum doit être un entier (reçu « %s »).")
                    % entry_num))
            if row_map["CompNumMvt"] and \
                    not row_map["CompNumMvt"].isdigit():
                errors.append(self._error(
                    pos, "CompNumMvt", "format", "error",
                    _("CompNumMvt doit être un entier (reçu « %s »).")
                    % row_map["CompNumMvt"]))
            if row_map["AccountNum"] and \
                    not row_map["AccountNum"].isdigit():
                errors.append(self._error(
                    pos, "AccountNum", "format", "error",
                    _("AccountNum doit être numérique (reçu « %s »).")
                    % row_map["AccountNum"]))

            # Dates
            for field_name in DATE_FIELDS:
                value = row_map[field_name]
                if value and not _valid_date(value):
                    errors.append(self._error(
                        pos, field_name, "format", "error",
                        _("%s doit être une date AAAAMMJJ valide "
                          "(reçu « %s »).") % (field_name, value)))
            if row_map["ValidDate"] and row_map["EcritureDate"] and \
                    _valid_date(row_map["ValidDate"]) and \
                    _valid_date(row_map["EcritureDate"]) and \
                    row_map["ValidDate"] < row_map["EcritureDate"]:
                errors.append(self._error(
                    pos, "ValidDate", "coherence", "error",
                    _("ValidDate antérieure à EcritureDate.")))
            if row_map["EcritureLet"] and not row_map["DateLet"]:
                errors.append(self._error(
                    pos, "DateLet", "coherence", "warning",
                    _("EcritureLet renseigné sans DateLet.")))

            # Montants
            debit = _parse_amount(row_map["Debit"])
            credit = _parse_amount(row_map["Credit"])
            if debit is None:
                errors.append(self._error(
                    pos, "Debit", "format", "error",
                    _("Debit invalide (reçu « %s »).") % row_map["Debit"]))
                debit = 0.0
            if credit is None:
                errors.append(self._error(
                    pos, "Credit", "format", "error",
                    _("Credit invalide (reçu « %s »).") % row_map["Credit"]))
                credit = 0.0
            if debit < 0 or credit < 0:
                errors.append(self._error(
                    pos, "Debit,Credit", "format", "error",
                    _("Montants négatifs interdits.")))
            if debit > 0 and credit > 0:
                errors.append(self._error(
                    pos, "Debit,Credit", "coherence", "warning",
                    _("Débit et crédit tous deux positifs sur la même "
                      "ligne.")))
            if debit == 0 and credit == 0:
                errors.append(self._error(
                    pos, "Debit,Credit", "coherence", "warning",
                    _("Ligne à montant nul.")))
            total_debit += debit
            total_credit += credit

            # Unicité (CodeJournal, EcritureDate, EcritureNum)
            key = (row_map["CodeJournal"], row_map["EcritureDate"],
                   entry_num)
            if all(key) and key in seen_keys:
                errors.append(self._error(
                    pos, "EcritureNum", "sequence", "error",
                    _("Écriture dupliquée %s/%s/%s.")
                    % (row_map["CodeJournal"], row_map["EcritureDate"],
                       entry_num)))
            if all(key):
                seen_keys.add(key)

            # Séquence croissante par journal
            journal = row_map["CodeJournal"]
            if journal and entry_num.isdigit():
                if journal in last_num and int(entry_num) <= last_num[journal]:
                    errors.append(self._error(
                        pos, "EcritureNum", "sequence", "error",
                        _("EcritureNum %s non croissant pour le journal "
                          "%s (précédent %d).")
                        % (entry_num, journal, last_num[journal])))
                last_num[journal] = max(last_num.get(journal, 0),
                                        int(entry_num))

            # Cohérence pièce / numéro de mouvement
            piece = row_map["CompPieceNum"]
            movement = row_map["CompNumMvt"]
            if piece and movement:
                if piece in piece_movement and \
                        piece_movement[piece] != movement:
                    errors.append(self._error(
                        pos, "CompNumMvt", "coherence", "warning",
                        _("La pièce %s a plusieurs numéros de mouvement "
                          "(%s, %s).") % (piece, piece_movement[piece],
                                          movement)))
                piece_movement.setdefault(piece, movement)

        # Balance globale
        gap = abs(total_debit - total_credit)
        if record_count and gap > 0.05:
            errors.append(self._error(
                0, "Debit,Credit", "balance", "error",
                _("Balance déséquilibrée : débit %.2f ≠ crédit %.2f "
                  "(écart %.2f).") % (total_debit, total_credit, gap)))

        # Pointage des anomalies sur les pièces comptables
        for error in errors:
            move_ref = pieces_by_line.get(error["line_number"], "")
            if not move_ref and error["line_number"] == 0 and pieces_by_line:
                refs = [r for r in pieces_by_line.values() if r]
                if refs:
                    move_ref = refs[0] if len(set(refs)) == 1 else ""
            error.setdefault("move_ref", move_ref)

        self.write({
            "record_count": record_count,
            "total_debit": total_debit,
            "total_credit": total_credit,
            "balance_gap": gap,
        })
        return errors

    def _error(self, line_no, field_name, code, severity, message):
        return {
            "validation_id": self.id,
            "line_number": line_no,
            "field_name": field_name,
            "code": code,
            "severity": severity,
            "message": message,
        }


class FecValidationError(models.Model):
    _name = "fec.validation.error"
    _description = "Anomalie de validation FEC"
    _order = "severity, line_number, id"

    validation_id = fields.Many2one(
        "fec.validation", required=True, ondelete="cascade", index=True)
    line_number = fields.Integer(string="Ligne du fichier")
    field_name = fields.Char(string="Champ")
    code = fields.Selection(
        [("length", "Longueur"), ("format", "Format"),
         ("balance", "Balance"), ("sequence", "Séquence"),
         ("missing", "Champ manquant"), ("coherence", "Cohérence")],
        string="Type")
    severity = fields.Selection(
        [("error", "Erreur"), ("warning", "Avertissement")],
        string="Sévérité", default="error")
    message = fields.Text(string="Message")
    move_ref = fields.Char(
        string="Référence de pièce",
        help="CompPieceNum de la ligne en anomalie, si identifiée.")

    def action_open_move(self):
        """Ouvre l'écriture comptable correspondant à la pièce."""
        self.ensure_one()
        move = self.env["account.move"].search(
            [("name", "=", self.move_ref)], limit=1)
        if not move:
            return {"type": "ir.actions.act_window_close"}
        return {
            "type": "ir.actions.act_window",
            "res_model": "account.move",
            "res_id": move.id,
            "view_mode": "form",
            "target": "current",
        }
