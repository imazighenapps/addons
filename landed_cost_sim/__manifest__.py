# -*- coding: utf-8 -*-
{
    "name": "Landed Cost Sim",
    "version": "18.0.1.0.0",
    "category": "Purchase/Purchase",
    "summary": "Manage suppliers, purchase orders and receipts with real-time cost control.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["purchase", "stock", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/landed_cost_sim_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
