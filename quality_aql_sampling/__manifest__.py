# -*- coding: utf-8 -*-
{
    "name": "Quality Aql Sampling",
    "version": "20.0.1.0.0",
    "category": "Manufacturing/Manufacturing",
    "summary": "Standardize bills of materials, quality checks and shop-floor execution in Odoo.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["stock", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/quality_aql_sampling_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
