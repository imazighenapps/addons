# -*- coding: utf-8 -*-
{
    "name": "Quality Equipment Qualification",
    "version": "19.0.1.0.0",
    "category": "Manufacturing/Manufacturing",
    "summary": "Standardize bills of materials, quality checks and shop-floor execution in Odoo.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["maintenance", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/quality_equipment_qualification_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
