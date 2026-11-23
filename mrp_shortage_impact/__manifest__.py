# -*- coding: utf-8 -*-
{
    "name": "Mrp Shortage Impact",
    "version": "20.0.1.0.0",
    "category": "Manufacturing/Manufacturing",
    "summary": "Plan production, track work orders and control costs across your manufacturing chain.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["mrp", "stock", "sale", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/mrp_shortage_impact_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
