# -*- coding: utf-8 -*-
{
    "name": "Mrp Customer Drawing Revisions",
    "version": "20.0.1.0.0",
    "category": "Manufacturing/Manufacturing",
    "summary": "Give production teams real-time control over capacity, costs and delivery dates.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["mrp", "sale", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/mrp_customer_drawing_revisions_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
