# -*- coding: utf-8 -*-
{
    "name": "Bank Balance Alerts",
    "version": "19.0.1.0.0",
    "category": "Accounting/Accounting",
    "summary": "Automate accounting controls, journal entries and financial reporting with full traceability.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["account", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/bank_balance_alerts_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
