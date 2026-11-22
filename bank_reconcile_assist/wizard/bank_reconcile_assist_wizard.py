# -*- coding: utf-8 -*-
import json
from datetime import date

from odoo import api, fields, models
from odoo.exceptions import UserError


class BankReconcileAssistWizard(models.TransientModel):
    _name = "bank.reconcile.assist.wizard"
    _description = "Assistant de rapprochement bancaire"

    company_id = fields.Many2one(
        "res.company", string="Société", required=True,
        default=lambda s: s.env.company)
    journal_id = fields.Many2one(
        "account.journal", string="Journal bancaire", required=True,
        domain="[('type', '=', 'bank'), ('company_id', '=', company_id)]")
    date_from = fields.Date(string="Du", required=True,
                            default=lambda s: date(date.today().year, date.today().month, 1))
    date_to = fields.Date(string="Au", required=True, default=fields.Date.context_today)
    amount_tolerance = fields.Float(string="Tolérance montant", default=0.0)
    line_ids = fields.One2many(
        "bank.reconcile.assist.line", "wizard_id", string="Propositions")
    computed = fields.Boolean(default=False)
    matched_count = fields.Integer(string="Rapprochés", compute="_compute_stats")
    pending_count = fields.Integer(string="En attente", compute="_compute_stats")

    @api.depends("line_ids.state")
    def _compute_stats(self):
        for wiz in self:
            wiz.matched_count = len(wiz.line_ids.filtered(lambda l: l.state == "matched"))
            wiz.pending_count = len(wiz.line_ids.filtered(lambda l: l.state == "proposal"))

    def _statement_lines_domain(self):
        return [
            ("journal_id", "=", self.journal_id.id),
            ("date", ">=", self.date_from),
            ("date", "<=", self.date_to),
            ("company_id", "=", self.company_id.id),
            ("is_reconciled", "=", False),
        ]

    def _candidate_move_lines(self, st_line):
        """Lignes d'écriture ouvertes candidates (recevable/payable) pour un relevé."""
        domain = [
            ("company_id", "=", self.company_id.id),
            ("reconciled", "=", False),
            ("account_id.reconcile", "=", True),
            ("parent_state", "=", "posted"),
            ("account_id.account_type", "in", ("asset_receivable", "liability_payable")),
        ]
        candidates = self.env["account.move.line"].search(domain, limit=500)
        # pré-filtre par montant compatible (même sens/valeur absolue proche)
        res = self.env["account.move.line"]
        for ml in candidates:
            residual = ml.amount_residual_currency if ml.currency_id else ml.amount_residual
            if not residual:
                continue
            if abs(abs(residual) - abs(st_line.amount)) <= (self.amount_tolerance or 0.01):
                res |= ml
        return res

    def _score(self, st_line, ml, rules):
        score = 0
        reasons = []
        residual = ml.amount_residual_currency if ml.currency_id else ml.amount_residual
        # montant
        if abs(abs(residual) - abs(st_line.amount)) < 0.01:
            score += 50
            reasons.append("montant exact")
        elif abs(abs(residual) - abs(st_line.amount)) <= (self.amount_tolerance or 0.0) + 0.01:
            score += 35
            reasons.append("montant dans tolérance")
        # partenaire
        if st_line.partner_id and ml.partner_id and st_line.partner_id == ml.partner_id:
            score += 30
            reasons.append("partenaire identique")
        # référence/libellé
        label = (st_line.payment_ref or "").lower()
        ref = (ml.move_id.name or ml.ref or "").lower()
        if label and (label in ref or ref in label):
            score += 15
            reasons.append("référence correspondante")
        # règles
        for rule in rules:
            ok, rscore = rule._matches_statement_line(st_line)
            if ok and rscore:
                score += int(rscore * 0.2)
                reasons.append("règle:%s" % rule.name)
                if not rule.amount_in_tolerance(st_line.amount, residual):
                    score -= 10
        return min(score, 100), ", ".join(reasons)

    def action_compute(self):
        self.ensure_one()
        st_lines = self.env["account.bank.statement.line"].search(
            self._statement_lines_domain(), order="date, id")
        if not st_lines:
            raise UserError("Aucune ligne de relevé non rapprochée trouvée pour la période.")
        rules = self.env["bank.reconcile.rule"].search([
            ("active", "=", True),
            ("company_id", "=", self.company_id.id),
            "|", ("journal_id", "=", False), ("journal_id", "=", self.journal_id.id),
        ])
        self.line_ids.unlink()
        vals_list = []
        for st in st_lines:
            candidates = self._candidate_move_lines(st)
            best = None
            for ml in candidates:
                sc, reason = self._score(st, ml, rules)
                if best is None or sc > best[0]:
                    best = (sc, ml, reason)
            if best and best[0] >= 20:
                sc, ml, reason = best
                vals_list.append({
                    "wizard_id": self.id,
                    "statement_line_id": st.id,
                    "move_line_id": ml.id,
                    "score": sc,
                    "reason": reason,
                    "state": "proposal",
                })
            else:
                vals_list.append({
                    "wizard_id": self.id,
                    "statement_line_id": st.id,
                    "score": 0,
                    "reason": "Aucun appariement trouvé",
                    "state": "no_match",
                })
        self.env["bank.reconcile.assist.line"].create(vals_list)
        self.computed = True
        return {
            "type": "ir.actions.act_window",
            "res_model": self._name,
            "res_id": self.id,
            "view_mode": "form",
            "target": "new",
        }

    def action_apply_selected(self):
        self.ensure_one()
        to_apply = self.line_ids.filtered(
            lambda l: l.selected and l.state == "proposal" and l.move_line_id)
        if not to_apply:
            raise UserError("Sélectionnez au moins une proposition à appliquer.")
        applied = 0
        for line in to_apply:
            try:
                st = line.statement_line_id
                ml = line.move_line_id
                if st.is_reconciled:
                    line.state = "skipped"
                    line.note = "Déjà rapproché"
                    continue
                # Associer le partenaire si manquant
                if not st.partner_id and ml.partner_id:
                    st.partner_id = ml.partner_id
                # Tenter la réconciliation standard Odoo 17+/20 via le widget/engine si dispo
                # Fallback: rapprocher les lignes comptables directement si possible
                st_line_aml = st.line_ids.filtered(lambda x: not x.reconciled and x.account_id.reconcile)
                target = ml
                if not target.reconciled and st_line_aml and target.account_id.reconcile:
                    (st_line_aml | target).reconcile()
                    line.state = "matched"
                    applied += 1
                else:
                    line.state = "error"
                    line.note = "Réconciliation comptable impossible (lignes non réconciliables)"
            except Exception as e:
                line.state = "error"
                line.note = str(e)[:200]
        return {
            "type": "ir.actions.act_window",
            "res_model": self._name,
            "res_id": self.id,
            "view_mode": "form",
            "target": "new",
        }

    def action_progress_report(self):
        """Rapport d'avancement du mois pour le journal sélectionné."""
        self.ensure_one()
        start = date(self.date_to.year, self.date_to.month, 1)
        domain = [
            ("journal_id", "=", self.journal_id.id),
            ("date", ">=", start),
            ("date", "<=", self.date_to),
            ("company_id", "=", self.company_id.id),
        ]
        total = self.env["account.bank.statement.line"].search_count(domain)
        done = self.env["account.bank.statement.line"].search_count(
            domain + [("is_reconciled", "=", True)])
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "Avancement rapprochement",
                "message": "Journal %s — %s/%s lignes rapprochées (%s%%) sur %s/%s."
                % (self.journal_id.display_name, done, total,
                   int(done * 100 / total) if total else 0,
                   start, self.date_to),
                "sticky": False,
                "type": "success" if total and done == total else "warning",
            },
        }


class BankReconcileAssistLine(models.TransientModel):
    _name = "bank.reconcile.assist.line"
    _description = "Proposition de rapprochement"
    _order = "score desc, id"

    wizard_id = fields.Many2one(
        "bank.reconcile.assist.wizard", required=True, ondelete="cascade")
    statement_line_id = fields.Many2one(
        "account.bank.statement.line", string="Ligne de relevé", required=True, readonly=True)
    st_date = fields.Date(related="statement_line_id.date", string="Date", readonly=True)
    st_label = fields.Char(related="statement_line_id.payment_ref", string="Libellé", readonly=True)
    st_amount = fields.Monetary(
        related="statement_line_id.amount", string="Montant relevé", readonly=True)
    currency_id = fields.Many2one(related="statement_line_id.currency_id", readonly=True)
    move_line_id = fields.Many2one(
        "account.move.line", string="Écriture proposée", readonly=True)
    move_ref = fields.Char(related="move_line_id.move_id.name", string="Pièce", readonly=True)
    ml_partner = fields.Many2one(related="move_line_id.partner_id", string="Partenaire", readonly=True)
    ml_residual = fields.Monetary(
        string="Résiduel", compute="_compute_residual", currency_field="currency_id")
    score = fields.Integer(string="Score", readonly=True)
    reason = fields.Char(string="Motif", readonly=True)
    selected = fields.Boolean(string="Appliquer", default=True)
    state = fields.Selection([
        ("proposal", "Proposition"),
        ("matched", "Rapproché"),
        ("no_match", "Sans correspondance"),
        ("skipped", "Ignoré"),
        ("error", "Erreur"),
    ], string="État", default="proposal", readonly=True)
    note = fields.Char(string="Note", readonly=True)

    @api.depends("move_line_id", "move_line_id.amount_residual")
    def _compute_residual(self):
        for line in self:
            ml = line.move_line_id
            if ml:
                line.ml_residual = ml.amount_residual_currency if ml.currency_id else ml.amount_residual
            else:
                line.ml_residual = 0.0
