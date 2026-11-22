# -*- coding: utf-8 -*-
{
    "name": "Supplier Item Crossref",
    "version": "19.0.1.0.0",
    "category": "Purchase/Purchase",
    "summary": "Give purchasing teams full visibility over demand, prices and supplier performance.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["purchase", "product", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/supplier_item_crossref_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
