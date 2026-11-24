# -*- coding: utf-8 -*-
{
    "name": "Price List Versioning",
    "version": "20.0.1.0.0",
    "category": "Purchase/Purchase",
    "summary": "Track pricing, lists and versioning in a dedicated Odoo workspace, from intake to reporting.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["purchase", "product", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/price_list_versioning_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nPrice List Versioning\n=====================\nTrack pricing, lists and versioning in a dedicated Odoo workspace, from intake to reporting.\n\nFeatures:\n---------\n* Pricing\n* Lists\n* Versioning\n* Supplier records\n* Purchase approvals\n* Cost control\n* Receipt visibility\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
