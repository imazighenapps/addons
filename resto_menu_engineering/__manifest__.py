# -*- coding: utf-8 -*-
{
    "name": "Resto Menu Engineering",
    "version": "20.0.1.0.0",
    "category": "Productivity/Productivity",
    "summary": "Automate repetitive tasks and keep teams aligned with structured Odoo workflows.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["point_of_sale", "account", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/resto_menu_engineering_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
