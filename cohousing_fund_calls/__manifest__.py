# -*- coding: utf-8 -*-
{
    "name": "Cohousing Fund Calls",
    "version": "18.0.1.0.0",
    "category": "Productivity/Productivity",
    "summary": "Automate repetitive tasks and keep teams aligned with structured Odoo workflows.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["account", "sale", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/cohousing_fund_calls_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
