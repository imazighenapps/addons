# -*- coding: utf-8 -*-
{
    "name": "Savings Pipeline Desk",
    "version": "19.0.1.0.0",
    "category": "Purchase/Purchase",
    "summary": "Manage suppliers, purchase orders and receipts with real-time cost control.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["purchase", "account", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/savings_pipeline_desk_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
