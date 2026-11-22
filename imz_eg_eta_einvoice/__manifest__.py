# -*- coding: utf-8 -*-
{
    "name": "Eg Eta Einvoice",
    "version": "20.0.1.0.0",
    "category": "Accounting",
    "summary": "Reconcile accounts, monitor balances and audit every financial entry from one Odoo workspace.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["account", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/eg_eta_einvoice_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
