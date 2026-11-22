# -*- coding: utf-8 -*-
"""Profils pays SAF-T et mappings comptes/taxes."""
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

# Énumération AccountType de la spécification OECD SAF-T
SAFT_ACCOUNT_TYPES = [
    ("SalesRevenue", "Ventes"),
    ("PurchasesCostOfMaterials", "Achats (coût des matières)"),
    ("PersonnelExpenses", "Charges de personnel"),
    ("Depreciation", "Amortissements"),
    ("OtherOperatingExpenses", "Autres charges d'exploitation"),
    ("OtherOperatingIncome", "Autres produits d'exploitation"),
    ("FinancialExpenses", "Charges financières"),
    ("FinancialIncome", "Produits financiers"),
    ("Capital", "Capital"),
    ("PersonalCustomers", "Clients"),
    ("PersonalSuppliers", "Fournisseurs"),
    ("OtherDebtors", "Autres débiteurs"),
    ("OtherCreditors", "Autres créditeurs"),
    ("Stock", "Stocks"),
    ("OpeningBalanceSheet", "Bilan d'ouverture"),
    ("ClosingBalanceSheet", "Bilan de clôture"),
    ("CurrentAssets", "Actif courant"),
    ("FixedAssets", "Actif immobilisé"),
    ("Equity", "Capitaux propres"),
    ("Taxes", "Taxes"),
]

# Fallback par groupe interne Odoo -> AccountType SAF-T
INTERNAL_GROUP_FALLBACK = {
    "income": "SalesRevenue",
    "expense": "OtherOperatingExpenses",
    "asset": "CurrentAssets",
    "liability": "OtherCreditors",
    "equity": "Capital",
    "off": "",
}


class SaftCountryProfile(models.Model):
    _name = "saft.country.profile"
    _description = "Profil pays SAF-T"
    _order = "sequence, id"

    name = fields.Char(string="Nom du profil", required=True)
    sequence = fields.Integer(default=10)
    country_id = fields.Many2one(
        "res.country", string="Pays", required=True)
    country_code = fields.Char(
        related="country_id.code", readonly=True)
    namespace = fields.Char(
        string="Namespace XML", required=True,
        default="urn:OECD:StandardAuditFile-Taxation:1.0",
        help="Namespace par défaut du fichier AuditFile pour ce pays.")
    schema_version = fields.Char(
        string="Version de schéma", required=True, default="1.0")
    tax_accounting_basis = fields.Char(
        string="Base comptable fiscale", default="Financeiro")
    require_explicit_account_map = fields.Boolean(
        string="Mapping explicite exigé",
        help="Signale en avertissement les comptes sans ligne de mapping "
             "explicite (le type par groupe interne reste appliqué).")
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company", string="Société", default=lambda self: self.env.company)
    account_map_ids = fields.One2many(
        "saft.account.map", "profile_id", string="Mappings de comptes")
    tax_map_ids = fields.One2many(
        "saft.tax.map", "profile_id", string="Mappings de taxes")

    _sql_constraints = [
        ("saft_profile_country_company_uniq",
         "unique(country_id, company_id)",
         "Un seul profil SAF-T par pays et société."),
    ]

    def account_type_for(self, account):
        """AccountType SAF-T d'un compte : mapping explicite puis fallback."""
        self.ensure_one()
        mapping = self.account_map_ids.filtered(
            lambda m: m.account_id == account)
        if mapping:
            return mapping[0].saft_account_type
        return INTERNAL_GROUP_FALLBACK.get(
            account.internal_group or "", "")


class SaftAccountMap(models.Model):
    _name = "saft.account.map"
    _description = "Mapping SAF-T de comptes"
    _order = "account_id, id"

    profile_id = fields.Many2one(
        "saft.country.profile", required=True, ondelete="cascade", index=True)
    account_id = fields.Many2one(
        "account.account", string="Compte", required=True,
        ondelete="cascade")
    saft_account_type = fields.Selection(
        SAFT_ACCOUNT_TYPES, string="AccountType SAF-T", required=True)

    @api.constrains("profile_id", "account_id")
    def _check_unique_account(self):
        for mapping in self:
            if len(mapping.profile_id.account_map_ids.filtered(
                    lambda m: m.account_id == mapping.account_id)) > 1:
                raise ValidationError(_(
                    "Le compte %s est déjà mappé dans ce profil.")
                    % mapping.account_id.display_name)

    _sql_constraints = [
        ("saft_account_map_uniq", "unique(profile_id, account_id)",
         "Un seul mapping par compte et profil SAF-T."),
    ]


class SaftTaxMap(models.Model):
    _name = "saft.tax.map"
    _description = "Mapping SAF-T de taxes"
    _order = "tax_id, id"

    profile_id = fields.Many2one(
        "saft.country.profile", required=True, ondelete="cascade", index=True)
    tax_id = fields.Many2one(
        "account.tax", string="Taxe", required=True, ondelete="cascade")
    saft_tax_code = fields.Char(
        string="Code SAF-T", required=True,
        help="Code de taxe tel qu'attendu par l'administration du pays.")
    saft_tax_type = fields.Selection(
        [("VAT", "VAT"), ("Other", "Other")],
        string="Type", default="VAT", required=True)
    saft_tax_rate = fields.Float(
        string="Taux (%)", digits=(6, 4),
        help="Taux attendu par l'administration (par défaut : taux Odoo).")

    @api.constrains("profile_id", "tax_id")
    def _check_unique_tax(self):
        for mapping in self:
            if len(mapping.profile_id.tax_map_ids.filtered(
                    lambda m: m.tax_id == mapping.tax_id)) > 1:
                raise ValidationError(_(
                    "La taxe %s est déjà mappée dans ce profil.")
                    % mapping.tax_id.display_name)

    _sql_constraints = [
        ("saft_tax_map_uniq", "unique(profile_id, tax_id)",
         "Un seul mapping par taxe et profil SAF-T."),
    ]
