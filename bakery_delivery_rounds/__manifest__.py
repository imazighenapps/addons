# -*- coding: utf-8 -*-
{
    "name": "Bakery Delivery Rounds",
    "version": "20.0.1.0.0",
    "category": "Productivity/Productivity",
    "summary": "Automate repetitive tasks and keep teams aligned with structured Odoo workflows.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["sale", "stock", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/bakery_delivery_rounds_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
