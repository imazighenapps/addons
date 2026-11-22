# -*- coding: utf-8 -*-
{
    "name": "Product Compat Rules",
    "version": "20.0.1.0.0",
    "category": "Sales/Sales",
    "summary": "Manage pipelines, customer follow-ups and sales performance with real-time visibility.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["sale", "product", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/product_compat_rules_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
