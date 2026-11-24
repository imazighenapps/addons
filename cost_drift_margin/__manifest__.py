# -*- coding: utf-8 -*-
{
    "name": "Cost Drift Margin",
    "version": "20.0.1.0.0",
    "category": "Purchase/Purchase",
    "summary": "Cost Drift Margin keeps cost tracking, drift and margins under control in Odoo, with workflow statuses and exports.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["purchase", "sale", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/cost_drift_margin_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nCost Drift Margin\n=================\nCost Drift Margin keeps cost tracking, drift and margins under control in Odoo, with workflow statuses and exports.\n\nFeatures:\n---------\n* Cost tracking\n* Drift\n* Margins\n* Supplier records\n* Purchase approvals\n* Cost control\n* Receipt visibility\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
