# -*- coding: utf-8 -*-
{
    "name": "Energy Certificate Desk",
    "version": "20.0.1.0.0",
    "category": "Accounting/Accounting",
    "summary": "Automate accounting controls, journal entries and financial reporting with full traceability.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["account", "sale", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/energy_certificate_desk_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
