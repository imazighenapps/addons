# -*- coding: utf-8 -*-
{
    "name": "Loading Order Desk",
    "version": "20.0.1.0.0",
    "category": "Inventory/Inventory",
    "summary": "Track loading and orders in a dedicated Odoo workspace, from intake to reporting.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["stock", "sale", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/loading_order_desk_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nLoading Order Desk\n==================\nTrack loading and orders in a dedicated Odoo workspace, from intake to reporting.\n\nFeatures:\n---------\n* Loading\n* Orders\n* Dedicated workspace\n* Structured records\n* Workflow statuses\n* Role-based access\n* Grouped views\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
