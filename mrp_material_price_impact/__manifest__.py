# -*- coding: utf-8 -*-
{
    "name": "Mrp Material Price Impact",
    "version": "18.0.1.0.0",
    "category": "Manufacturing/Manufacturing",
    "summary": "Give production teams real-time control over capacity, costs and delivery dates.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["mrp", "purchase", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/mrp_material_price_impact_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
