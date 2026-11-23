# -*- coding: utf-8 -*-
{
    "name": "Ma Fiscal Pack",
    "version": "20.0.1.0.0",
    "category": "Accounting",
    "summary": "Give finance teams a focused Odoo app for reconciliation, analysis and compliant reporting.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["account", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/ma_fiscal_pack_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
