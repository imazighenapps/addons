# -*- coding: utf-8 -*-
{
    "name": "Multi Drop Delivery",
    "version": "20.0.1.0.0",
    "category": "Sales/Sales",
    "summary": "Qualify leads, accelerate quotations and close more deals from a single Odoo workspace.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["sale", "stock", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/multi_drop_delivery_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
