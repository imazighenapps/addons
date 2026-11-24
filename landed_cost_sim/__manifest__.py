# -*- coding: utf-8 -*-
{
    "name": "Landed Cost Sim",
    "version": "20.0.1.0.0",
    "category": "Purchase/Purchase",
    "summary": "Landed Cost Sim keeps landed, cost tracking and SIM cards under control in Odoo, with workflow statuses and exports.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["purchase", "stock", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/landed_cost_sim_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nLanded Cost Sim\n===============\nLanded Cost Sim keeps landed, cost tracking and SIM cards under control in Odoo, with workflow statuses and exports.\n\nFeatures:\n---------\n* Landed\n* Cost tracking\n* SIM cards\n* Supplier records\n* Purchase approvals\n* Cost control\n* Receipt visibility\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
