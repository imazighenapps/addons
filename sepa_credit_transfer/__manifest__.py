# -*- coding: utf-8 -*-
{
    "name": "Sepa Credit Transfer",
    "version": "19.0.1.0.0",
    "category": "Accounting",
    "summary": "Automate accounting controls, journal entries and financial reporting with full traceability.",
    "description": """Sessions de paiement SEPA multi-factures, génération pain.001,
contrôles IBAN/BIC, identifiant unique, import des rejets pain.002 et historique.""",
    "author": "ImazighenApps",
    "website": "https://apps.odoo.com/",
    "license": "LGPL-3",
    "depends": ["account", "mail"],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "data/ir_sequence_data.xml",
        "views/sct_batch_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
