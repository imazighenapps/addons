# -*- coding: utf-8 -*-
{
    "name": "Intercompany Margin Elim",
    "version": "20.0.1.0.0",
    "category": "Accounting/Accounting",
    "summary": "Automate accounting controls, journal entries and financial reporting with full traceability.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["account", "stock", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/intercompany_margin_elim_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
