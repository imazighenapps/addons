# -*- coding: utf-8 -*-
{
    "name": "Sepa Mandate Lifecycle",
    "version": "18.0.1.0.0",
    "category": "Accounting",
    "summary": "Reconcile accounts, monitor balances and audit every financial entry from one Odoo workspace.",
    "description": """Registre de mandats avec cycle de vie complet, historique des RIB,
alertes d'expiration/révocation, pièce signée et piste d'audit.""",
    "author": "ImazighenApps",
    "website": "https://apps.odoo.com/",
    "license": "LGPL-3",
    "depends": ["account", "mail"],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "data/cron.xml",
        "views/mandate_lifecycle_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
