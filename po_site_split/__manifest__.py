# -*- coding: utf-8 -*-
{
    "name": "Po Site Split",
    "version": "20.0.1.0.0",
    "category": "Purchase/Purchase",
    "summary": "Track purchase orders, sites and splits in a dedicated Odoo workspace, from intake to reporting.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["purchase", "stock", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/po_site_split_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nPo Site Split\n=============\nTrack purchase orders, sites and splits in a dedicated Odoo workspace, from intake to reporting.\n\nFeatures:\n---------\n* Purchase orders\n* Sites\n* Splits\n* Supplier records\n* Purchase approvals\n* Cost control\n* Receipt visibility\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
