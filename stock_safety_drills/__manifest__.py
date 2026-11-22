# -*- coding: utf-8 -*-
{
    "name": "Stock Safety Drills",
    "version": "18.0.1.0.0",
    "category": "Inventory/Inventory",
    "summary": "Give logistics teams a focused Odoo app for faster, error-free stock movements.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["stock", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/stock_safety_drills_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
