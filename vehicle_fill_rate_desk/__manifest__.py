# -*- coding: utf-8 -*-
{
    "name": "Vehicle Fill Rate Desk",
    "version": "18.0.1.0.0",
    "category": "Inventory/Inventory",
    "summary": "Track stock levels, transfers and replenishment with real-time Odoo visibility.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["stock", "fleet", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/vehicle_fill_rate_desk_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
