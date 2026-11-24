# -*- coding: utf-8 -*-
{
    "name": "Savings Pipeline Desk",
    "version": "20.0.1.0.0",
    "category": "Purchase/Purchase",
    "summary": "Centralize savings and pipeline in one Odoo workspace, with role-based access and approvals.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["purchase", "account", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/savings_pipeline_desk_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nSavings Pipeline Desk\n=====================\nCentralize savings and pipeline in one Odoo workspace, with role-based access and approvals.\n\nFeatures:\n---------\n* Savings\n* Pipeline\n* Supplier records\n* Purchase approvals\n* Cost control\n* Receipt visibility\n* Vendor comparison\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
