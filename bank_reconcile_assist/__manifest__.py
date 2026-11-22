# -*- coding: utf-8 -*-
{
    "name": "Bank Reconcile Assist",
    "version": "20.0.1.0.0",
    "category": "Accounting",
    "summary": "Give finance teams a focused Odoo app for reconciliation, analysis and compliant reporting.",
    "description": """
Rapprochement Bancaire Assisté
==============================
Accélère le rapprochement bancaire en Odoo Community :
- Règles d'auto-matching configurables (libellé, référence, montant, partenaire)
- Tolérances de montant (fixe ou pourcentage)
- Propositions de lettrage classées par score
- Application en un clic et gestion des écarts
- Rapport d'avancement mensuel
    """,
    "author": "ImazighenApps",
    "website": "https://apps.odoo.com/",
    "license": "LGPL-3",
    "depends": ["account"],
    "data": [
        "security/security.xml",
        "security/ir.access.csv",
        "views/bank_reconcile_rule_views.xml",
        "views/bank_reconcile_wizard_views.xml",
        "views/menus.xml",
        "report/reconcile_progress_report.xml",
    ],
    "application": False,
}
