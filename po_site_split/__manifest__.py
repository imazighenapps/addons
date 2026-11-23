# -*- coding: utf-8 -*-
{
    "name": "Po Site Split",
    "version": "20.0.1.0.0",
    "category": "Purchase/Purchase",
    "summary": "Manage suppliers, purchase orders and receipts with real-time cost control.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["purchase", "stock", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/po_site_split_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
