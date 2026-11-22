# -*- coding: utf-8 -*-
{
    "name": "Jp Invoice System Pack",
    "version": "19.0.1.0.0",
    "category": "Accounting",
    "summary": "Automate accounting controls, journal entries and financial reporting with full traceability.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["account", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/jp_invoice_system_pack_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
