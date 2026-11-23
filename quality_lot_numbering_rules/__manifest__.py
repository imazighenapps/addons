# -*- coding: utf-8 -*-
{
    "name": "Quality Lot Numbering Rules",
    "version": "19.0.1.0.0",
    "category": "Manufacturing/Manufacturing",
    "summary": "Give production teams real-time control over capacity, costs and delivery dates.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["mrp", "stock", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/quality_lot_numbering_rules_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
