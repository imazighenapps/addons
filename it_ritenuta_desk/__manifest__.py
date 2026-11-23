# -*- coding: utf-8 -*-
{
    "name": "It Ritenuta Desk",
    "version": "20.0.1.0.0",
    "category": "Accounting/Accounting",
    "summary": "Reconcile accounts, monitor balances and audit every financial entry from one Odoo workspace.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["account", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/it_ritenuta_desk_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
