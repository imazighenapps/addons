# -*- coding: utf-8 -*-
{
    "name": "Purchase Long Lead Watch",
    "version": "18.0.1.0.0",
    "category": "Manufacturing/Manufacturing",
    "summary": "Standardize bills of materials, quality checks and shop-floor execution in Odoo.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["purchase", "mrp", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/purchase_long_lead_watch_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
