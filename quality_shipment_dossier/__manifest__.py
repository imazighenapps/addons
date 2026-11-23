# -*- coding: utf-8 -*-
{
    "name": "Quality Shipment Dossier",
    "version": "19.0.1.0.0",
    "category": "Manufacturing/Manufacturing",
    "summary": "Standardize bills of materials, quality checks and shop-floor execution in Odoo.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["stock", "sale", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/quality_shipment_dossier_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
