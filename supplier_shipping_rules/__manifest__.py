# -*- coding: utf-8 -*-
{
    "name": "Supplier Shipping Rules",
    "version": "20.0.1.0.0",
    "category": "Purchase/Purchase",
    "summary": "Give purchasing teams full visibility over demand, prices and supplier performance.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["purchase", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/supplier_shipping_rules_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
