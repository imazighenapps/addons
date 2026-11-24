# -*- coding: utf-8 -*-
{
    "name": "Purchase Substitute Desk",
    "version": "20.0.1.0.0",
    "category": "Purchase/Purchase",
    "summary": "Track purchasing and substitute in a dedicated Odoo workspace, from intake to reporting.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["purchase", "product", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/purchase_substitute_desk_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nPurchase Substitute Desk\n========================\nTrack purchasing and substitute in a dedicated Odoo workspace, from intake to reporting.\n\nFeatures:\n---------\n* Purchasing\n* Substitute\n* Supplier records\n* Purchase approvals\n* Cost control\n* Receipt visibility\n* Vendor comparison\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
