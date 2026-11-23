# -*- coding: utf-8 -*-
{
    "name": "Competitor Price Log",
    "version": "20.0.1.0.0",
    "category": "Sales/Sales",
    "summary": "Qualify leads, accelerate quotations and close more deals from a single Odoo workspace.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["sale", "product", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/competitor_price_log_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
