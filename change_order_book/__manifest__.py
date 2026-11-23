# -*- coding: utf-8 -*-
{
    "name": "Change Order Book",
    "version": "20.0.1.0.0",
    "category": "Project/Project",
    "summary": "Plan tasks, track time and monitor project profitability from a single Odoo workspace.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["project", "sale", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/change_order_book_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
