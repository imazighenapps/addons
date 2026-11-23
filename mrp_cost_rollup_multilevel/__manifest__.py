# -*- coding: utf-8 -*-
{
    "name": "Mrp Cost Rollup Multilevel",
    "version": "19.0.1.0.0",
    "category": "Manufacturing/Manufacturing",
    "summary": "Standardize bills of materials, quality checks and shop-floor execution in Odoo.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["mrp", "account", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/mrp_cost_rollup_multilevel_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
