# -*- coding: utf-8 -*-
{
    "name": "Traffic Fine Desk",
    "version": "20.0.1.0.0",
    "category": "Inventory/Inventory",
    "summary": "Give logistics teams a focused Odoo app for faster, error-free stock movements.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["fleet", "account", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/traffic_fine_desk_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
