# -*- coding: utf-8 -*-
{
    "name": "Sale Penalty Registry",
    "version": "20.0.1.0.0",
    "category": "Manufacturing/Manufacturing",
    "summary": "Plan production, track work orders and control costs across your manufacturing chain.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["sale", "account", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/sale_penalty_registry_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
