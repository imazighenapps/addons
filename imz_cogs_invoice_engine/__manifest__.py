# -*- coding: utf-8 -*-
{
    "name": "Cogs Invoice Engine",
    "version": "19.0.1.0.0",
    "category": "Accounting/Accounting",
    "summary": "Automate accounting controls, journal entries and financial reporting with full traceability.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["account", "stock", "sale", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/cogs_invoice_engine_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
