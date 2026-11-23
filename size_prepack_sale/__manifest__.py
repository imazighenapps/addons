# -*- coding: utf-8 -*-
{
    "name": "Size Prepack Sale",
    "version": "20.0.1.0.0",
    "category": "Sales/Sales",
    "summary": "Give sales teams a focused Odoo app to convert opportunities into recurring revenue.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["sale", "product", "stock", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/size_prepack_sale_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
