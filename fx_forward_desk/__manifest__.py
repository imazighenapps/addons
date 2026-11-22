# -*- coding: utf-8 -*-
{
    "name": "Fx Forward Desk",
    "version": "18.0.1.0.0",
    "category": "Accounting",
    "summary": "Reconcile accounts, monitor balances and audit every financial entry from one Odoo workspace.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["account", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/fx_forward_desk_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
