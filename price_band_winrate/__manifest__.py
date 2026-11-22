# -*- coding: utf-8 -*-
{
    "name": "Price Band Winrate",
    "version": "18.0.1.0.0",
    "category": "Sales/Sales",
    "summary": "Give sales teams a focused Odoo app to convert opportunities into recurring revenue.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["sale", "crm", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/price_band_winrate_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
