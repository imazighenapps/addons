# -*- coding: utf-8 -*-
{
    "name": "Delivery Frequency Plan",
    "version": "20.0.1.0.0",
    "category": "Inventory/Inventory",
    "summary": "Track stock levels, transfers and replenishment with real-time Odoo visibility.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["sale", "stock", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/delivery_frequency_plan_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
