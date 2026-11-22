# -*- coding: utf-8 -*-
{
    "name": "Financial Reports Community",
    "version": "19.0.1.0.0",
    "category": "Accounting",
    "summary": "Automate accounting controls, journal entries and financial reporting with full traceability.",
    "description": """
États Financiers Community
===========================
Fournit à Odoo Community les états financiers qui y manquent :
compte de résultat, bilan, état de trésorerie, balance et rapport
personnalisés, avec comparaison de périodes, hiérarchie de comptes
(groupes comptables), détail par compte, export PDF et CSV.

- Définitions d'états paramétrables (lignes, sous-totaux, signes)
- Agrégation réelle sur account.move.line (écritures postées)
- Comparaison entre deux périodes et variation
- Export PDF (QWeb) et CSV
    """,
    "author": "ImazighenApps",
    "website": "https://apps.odoo.com/",
    "license": "LGPL-3",
    "depends": ["account"],
    "data": [
        "security/security.xml",
        "views/menus.xml",
        "views/financial_report_views.xml",
        "report/financial_report_report.xml",
        "report/financial_report_templates.xml",
    ],
    "application": True,
}
