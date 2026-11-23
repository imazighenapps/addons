# -*- coding: utf-8 -*-
{
    "name": "Supplier Screening Guard",
    "version": "19.0.1.0.0",
    "category": "Purchase/Purchase",
    "summary": "Give purchasing teams full visibility over demand, prices and supplier performance.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["purchase", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/supplier_screening_guard_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
