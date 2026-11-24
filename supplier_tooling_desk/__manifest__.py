# -*- coding: utf-8 -*-
{
    "name": "Supplier Tooling Desk",
    "version": "20.0.1.0.0",
    "category": "Purchase/Purchase",
    "summary": "Track supplier records and tooling in a dedicated Odoo workspace, from intake to reporting.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["purchase", "product", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/supplier_tooling_desk_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nSupplier Tooling Desk\n=====================\nTrack supplier records and tooling in a dedicated Odoo workspace, from intake to reporting.\n\nFeatures:\n---------\n* Supplier records\n* Tooling\n* Purchase approvals\n* Cost control\n* Receipt visibility\n* Vendor comparison\n* Procurement history\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
