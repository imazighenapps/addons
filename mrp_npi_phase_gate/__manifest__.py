# -*- coding: utf-8 -*-
{
    "name": "Mrp Npi Phase Gate",
    "version": "20.0.1.0.0",
    "category": "Manufacturing/Manufacturing",
    "summary": "Standardize bills of materials, quality checks and shop-floor execution in Odoo.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["mrp", "project", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/mrp_npi_phase_gate_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
