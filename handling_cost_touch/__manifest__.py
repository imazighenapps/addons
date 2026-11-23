# -*- coding: utf-8 -*-
{
    "name": "Handling Cost Touch",
    "version": "19.0.1.0.0",
    "category": "Inventory/Inventory",
    "summary": "Control warehouse operations, lot traceability and inventory accuracy from one place.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["stock", "hr", "account", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/handling_cost_touch_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
