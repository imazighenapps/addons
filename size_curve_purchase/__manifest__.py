# -*- coding: utf-8 -*-
{
    "name": "Size Curve Purchase",
    "version": "20.0.1.0.0",
    "category": "Purchase/Purchase",
    "summary": "Manage suppliers, purchase orders and receipts with real-time cost control.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["purchase", "sale", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/size_curve_purchase_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
