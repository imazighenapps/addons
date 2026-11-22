# -*- coding: utf-8 -*-
{
    "name": "Pre Close Checks",
    "version": "20.0.1.0.0",
    "category": "Accounting/Accounting",
    "summary": "Give finance teams a focused Odoo app for reconciliation, analysis and compliant reporting.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["account", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/pre_close_checks_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
