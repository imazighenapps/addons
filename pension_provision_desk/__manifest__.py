# -*- coding: utf-8 -*-
{
    "name": "Pension Provision Desk",
    "version": "18.0.1.0.0",
    "category": "Accounting/Accounting",
    "summary": "Automate accounting controls, journal entries and financial reporting with full traceability.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["account", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/pension_provision_desk_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
