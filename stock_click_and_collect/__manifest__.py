# -*- coding: utf-8 -*-
{
    "name": "Stock Click and Collect",
    "version": "19.0.1.0.0",
    "category": "Inventory/Inventory",
    "summary": "Control warehouse operations, lot traceability and inventory accuracy from one place.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["stock", "sale", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/stock_click_and_collect_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
