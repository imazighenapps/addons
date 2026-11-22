# -*- coding: utf-8 -*-
{
    "name": "Pl Ksef Bridge",
    "version": "18.0.1.0.0",
    "category": "Accounting",
    "summary": "Reconcile accounts, monitor balances and audit every financial entry from one Odoo workspace.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["account", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/pl_ksef_bridge_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
