# -*- coding: utf-8 -*-
{
    "name": "Quality Heat Treatment Registry",
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
        "views/quality_heat_treatment_registry_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
