# -*- coding: utf-8 -*-
{
    "name": "Stock Inventory Placement",
    "version": "18.0.1.0.0",
    "category": "Inventory/Inventory",
    "summary": "Track stock levels, transfers and replenishment with real-time Odoo visibility.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["stock", "sale", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/stock_inventory_placement_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
