# -*- coding: utf-8 -*-
{
    "name": "Stock Accounting Reconcile",
    "version": "19.0.1.0.0",
    "category": "Accounting/Accounting",
    "summary": "Reconcile accounts, monitor balances and audit every financial entry from one Odoo workspace.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["account", "stock", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/stock_accounting_reconcile_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
