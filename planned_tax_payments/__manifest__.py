# -*- coding: utf-8 -*-
{
    "name": "Planned Tax Payments",
    "version": "19.0.1.0.0",
    "category": "Accounting/Accounting",
    "summary": "Give finance teams a focused Odoo app for reconciliation, analysis and compliant reporting.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["account", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/planned_tax_payments_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
