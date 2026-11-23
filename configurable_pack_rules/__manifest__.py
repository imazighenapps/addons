# -*- coding: utf-8 -*-
{
    "name": "Configurable Pack Rules",
    "version": "18.0.1.0.0",
    "category": "Sales/Sales",
    "summary": "Give sales teams a focused Odoo app to convert opportunities into recurring revenue.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["sale", "stock", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/configurable_pack_rules_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
