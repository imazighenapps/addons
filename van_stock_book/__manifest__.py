# -*- coding: utf-8 -*-
{
    "name": "Van Stock Book",
    "version": "19.0.1.0.0",
    "category": "Project/Project",
    "summary": "Plan tasks, track time and monitor project profitability from a single Odoo workspace.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["stock", "project", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/van_stock_book_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
