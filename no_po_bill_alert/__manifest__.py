# -*- coding: utf-8 -*-
{
    "name": "No Po Bill Alert",
    "version": "18.0.1.0.0",
    "category": "Accounting/Accounting",
    "summary": "Give finance teams a focused Odoo app for reconciliation, analysis and compliant reporting.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["account", "purchase", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/no_po_bill_alert_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
