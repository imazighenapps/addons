# -*- coding: utf-8 -*-
{
    "name": "Customer Early Discount",
    "version": "20.0.1.0.0",
    "category": "Accounting/Accounting",
    "summary": "Give finance teams a focused Odoo app for reconciliation, analysis and compliant reporting.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["account", "sale", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/customer_early_discount_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
