# -*- coding: utf-8 -*-
{
    "name": "Grni Aging Desk",
    "version": "18.0.1.0.0",
    "category": "Accounting/Accounting",
    "summary": "Give finance teams a focused Odoo app for reconciliation, analysis and compliant reporting.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["account", "stock", "purchase", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/grni_aging_desk_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
