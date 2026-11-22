# -*- coding: utf-8 -*-
{
    "name": "Sepa Direct Debit",
    "version": "20.0.1.0.0",
    "category": "Accounting",
    "summary": "Give finance teams a focused Odoo app for reconciliation, analysis and compliant reporting.",
    "description": """Cycle de prélèvement SEPA : registre de mandats, génération pain.008,
gestion des séquences et traitement des retours.""",
    "author": "ImazighenApps",
    "website": "https://apps.odoo.com/",
    "license": "LGPL-3",
    "depends": ["account", "mail"],
    "data": [
        "security/security.xml",
        "security/ir.access.csv",
        "data/ir_sequence_data.xml",
        "views/sdd_mandate_views.xml",
        "views/sdd_batch_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
