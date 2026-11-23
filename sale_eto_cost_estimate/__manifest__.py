# -*- coding: utf-8 -*-
{
    "name": "Sale Eto Cost Estimate",
    "version": "18.0.1.0.0",
    "category": "Manufacturing/Manufacturing",
    "summary": "Give production teams real-time control over capacity, costs and delivery dates.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["sale", "mrp", "purchase", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/sale_eto_cost_estimate_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
