# -*- coding: utf-8 -*-
from odoo import api, fields, models


class BankReconcileRule(models.Model):
    _name = "bank.reconcile.rule"
    _description = "Règle d'auto-rapprochement bancaire"
    _order = "sequence, id"

    name = fields.Char(string="Nom", required=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company", string="Société", default=lambda s: s.env.company, required=True)
    journal_id = fields.Many2one(
        "account.journal", string="Journal bancaire",
        domain="[('type', '=', 'bank'), ('company_id', '=', company_id)]")
    partner_id = fields.Many2one("res.partner", string="Partenaire imposé")
    label_contains = fields.Char(string="Libellé contient")
    ref_contains = fields.Char(string="Référence contient")
    amount_tolerance = fields.Float(string="Tolérance montant", default=0.0)
    tolerance_type = fields.Selection(
        [("fixed", "Montant fixe"), ("percent", "Pourcentage")],
        string="Type de tolérance", default="fixed", required=True)
    counterpart_account_id = fields.Many2one(
        "account.account", string="Compte de contrepartie (écart)")
    auto_apply = fields.Boolean(
        string="Application automatique",
        help="Appliquer automatiquement si le score atteint le seuil.")
    min_score = fields.Integer(string="Score minimum", default=80)

    def _matches_statement_line(self, st_line):
        """Retourne (match: bool, score: int 0-100)."""
        self.ensure_one()
        if self.journal_id and st_line.journal_id != self.journal_id:
            return False, 0
        score = 0
        checks = 0
        label = (st_line.payment_ref or st_line.name or "").lower()
        ref = (getattr(st_line, "ref", None) or "").lower()
        if self.label_contains:
            checks += 1
            if self.label_contains.lower() in label:
                score += 35
        if self.ref_contains:
            checks += 1
            if self.ref_contains.lower() in ref:
                score += 35
        if self.partner_id:
            checks += 1
            if st_line.partner_id == self.partner_id:
                score += 30
        # bonus montant exact géré côté appariement ; règle seule = critères textuels/partenaire
        if checks == 0:
            return True, 20
        return score > 0, min(score, 100)

    def amount_in_tolerance(self, amount_a, amount_b):
        self.ensure_one()
        diff = abs(abs(amount_a) - abs(amount_b))
        if self.tolerance_type == "percent":
            base = abs(amount_a) or 1.0
            return diff <= base * (self.amount_tolerance / 100.0)
        return diff <= self.amount_tolerance
