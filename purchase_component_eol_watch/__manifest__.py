# -*- coding: utf-8 -*-
{
    "name": "Purchase Component Eol Watch",
    "version": "20.0.1.0.0",
    "category": "Manufacturing/Manufacturing",
    "summary": "Run purchasing, components and eol end to end in Odoo, with structured records and audit-ready history.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["purchase", "mrp", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/purchase_component_eol_watch_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nPurchase Component Eol Watch\n============================\nRun purchasing, components and eol end to end in Odoo, with structured records and audit-ready history.\n\nFeatures:\n---------\n* Purchasing\n* Components\n* Eol\n* Supplier records\n* Purchase approvals\n* Cost control\n* Receipt visibility\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
