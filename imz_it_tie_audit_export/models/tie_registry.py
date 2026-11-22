# -*- coding: utf-8 -*-
"""Mapping des registres fiscaux italiens vers les journaux Odoo."""
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

TIE_REGISTRIES = [
    ("iva_vendite", "Registre IVA — Ventes"),
    ("iva_acquisti", "Registre IVA — Achats"),
    ("corrispettivi", "Corrispettivi di vendita"),
    ("generale", "Journal général"),
    ("cespiti", "Registre des amortissements"),
]


class TieRegistryMap(models.Model):
    _name = "tie.registry.map"
    _description = "Mapping registres fiscaux TIE"
    _order = "registry_code, id"

    name = fields.Char(
        string="Libellé", compute="_compute_name", store=True)
    company_id = fields.Many2one(
        "res.company", string="Société", required=True,
        default=lambda self: self.env.company)
    registry_code = fields.Selection(
        TIE_REGISTRIES, string="Registre fiscal", required=True)
    journal_ids = fields.Many2many(
        "account.journal", "tie_registry_map_journal_rel",
        "map_id", "journal_id", string="Journaux Odoo", required=True)

    _sql_constraints = [
        ("tie_registry_company_uniq", "unique(company_id, registry_code)",
         "Un seul mapping par registre fiscal et société."),
    ]

    @api.depends("registry_code")
    def _compute_name(self):
        labels = dict(TIE_REGISTRIES)
        for mapping in self:
            mapping.name = labels.get(mapping.registry_code, "")

    def journal_for(self, journal):
        """Code de registre d'un journal ("" si non mappé)."""
        for mapping in self:
            if journal in mapping.journal_ids:
                return mapping.registry_code
        return ""

    @api.constrains("company_id", "registry_code")
    def _check_unique_registry(self):
        for mapping in self:
            if self.search_count([
                ("company_id", "=", mapping.company_id.id),
                ("registry_code", "=", mapping.registry_code),
                ("id", "!=", mapping.id),
            ]):
                raise ValidationError(_(
                    "Un seul mapping par registre fiscal et société."))

    @api.constrains("journal_ids")
    def _check_journal_company(self):
        for mapping in self:
            wrong = mapping.journal_ids.filtered(
                lambda j: j.company_id != mapping.company_id)
            if wrong:
                raise ValidationError(_(
                    "Les journaux %s appartiennent à une autre société.")
                    % ", ".join(wrong.mapped("code")))


class ResCompany(models.Model):
    _inherit = "res.company"

    tie_registry_map_ids = fields.One2many(
        "tie.registry.map", "company_id",
        string="Mapping registres fiscaux TIE")
