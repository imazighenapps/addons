# -*- coding: utf-8 -*-
{
    "name": "Quality Coa Generator",
    "version": "20.0.1.0.0",
    "category": "Manufacturing/Manufacturing",
    "summary": "Plan production, track work orders and control costs across your manufacturing chain.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["stock", "sale", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/quality_coa_generator_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
