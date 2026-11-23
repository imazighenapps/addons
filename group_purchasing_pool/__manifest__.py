# -*- coding: utf-8 -*-
{
    "name": "Group Purchasing Pool",
    "version": "20.0.1.0.0",
    "category": "Purchase/Purchase",
    "summary": "Manage suppliers, purchase orders and receipts with real-time cost control.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["purchase", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/group_purchasing_pool_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
