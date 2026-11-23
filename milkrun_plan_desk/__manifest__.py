# -*- coding: utf-8 -*-
{
    "name": "Milkrun Plan Desk",
    "version": "20.0.1.0.0",
    "category": "Inventory/Inventory",
    "summary": "Track stock levels, transfers and replenishment with real-time Odoo visibility.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["stock", "purchase", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/milkrun_plan_desk_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
