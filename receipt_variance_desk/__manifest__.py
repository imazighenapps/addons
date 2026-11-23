# -*- coding: utf-8 -*-
{
    "name": "Receipt Variance Desk",
    "version": "19.0.1.0.0",
    "category": "Purchase/Purchase",
    "summary": "Manage suppliers, purchase orders and receipts with real-time cost control.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["stock", "purchase", "account", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/receipt_variance_desk_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
