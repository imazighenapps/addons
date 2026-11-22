# -*- coding: utf-8 -*-
{
    "name": "Purchase Component Eol Watch",
    "version": "20.0.1.0.0",
    "category": "Manufacturing/Manufacturing",
    "summary": "Give production teams real-time control over capacity, costs and delivery dates.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["purchase", "mrp", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/purchase_component_eol_watch_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
