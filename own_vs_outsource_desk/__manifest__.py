# -*- coding: utf-8 -*-
{
    "name": "Own Vs Outsource Desk",
    "version": "20.0.1.0.0",
    "category": "Inventory/Inventory",
    "summary": "Control warehouse operations, lot traceability and inventory accuracy from one place.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["fleet", "account", "stock", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/own_vs_outsource_desk_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
