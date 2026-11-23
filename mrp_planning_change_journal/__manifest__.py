# -*- coding: utf-8 -*-
{
    "name": "Mrp Planning Change Journal",
    "version": "20.0.1.0.0",
    "category": "Manufacturing/Manufacturing",
    "summary": "Standardize bills of materials, quality checks and shop-floor execution in Odoo.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["mrp", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/mrp_planning_change_journal_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
