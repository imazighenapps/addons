# -*- coding: utf-8 -*-
{
    "name": "Horse Boarding Book",
    "version": "20.0.1.0.0",
    "category": "Productivity/Productivity",
    "summary": "Automate repetitive tasks and keep teams aligned with structured Odoo workflows.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["sale", "account", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/horse_boarding_book_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
