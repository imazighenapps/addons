# -*- coding: utf-8 -*-
{
    "name": "Freight Tender Desk",
    "version": "20.0.1.0.0",
    "category": "Inventory/Inventory",
    "summary": "Track freight costs and tender in a dedicated Odoo workspace, from intake to reporting.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["stock", "purchase", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/freight_tender_desk_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nFreight Tender Desk\n===================\nTrack freight costs and tender in a dedicated Odoo workspace, from intake to reporting.\n\nFeatures:\n---------\n* Freight costs\n* Tender\n* Dedicated workspace\n* Structured records\n* Workflow statuses\n* Role-based access\n* Grouped views\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
