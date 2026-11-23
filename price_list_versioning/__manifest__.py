# -*- coding: utf-8 -*-
{
    "name": "Price List Versioning",
    "version": "20.0.1.0.0",
    "category": "Purchase/Purchase",
    "summary": "Automate procurement approvals and vendor follow-ups from one Odoo workspace.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["purchase", "product", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/price_list_versioning_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
