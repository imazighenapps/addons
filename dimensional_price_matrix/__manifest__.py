# -*- coding: utf-8 -*-
{
    "name": "Dimensional Price Matrix",
    "version": "20.0.1.0.0",
    "category": "Sales/Sales",
    "summary": "Manage pipelines, customer follow-ups and sales performance with real-time visibility.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["sale", "uom", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/dimensional_price_matrix_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
