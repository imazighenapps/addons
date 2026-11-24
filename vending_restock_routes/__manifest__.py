# -*- coding: utf-8 -*-
{
    "name": "Vending Restock Routes",
    "version": "20.0.1.0.0",
    "category": "Productivity/Productivity",
    "summary": "Centralize vending, restock and routes in one Odoo workspace, with role-based access and approvals.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["stock", "sale", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/vending_restock_routes_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nVending Restock Routes\n======================\nCentralize vending, restock and routes in one Odoo workspace, with role-based access and approvals.\n\nFeatures:\n---------\n* Vending\n* Restock\n* Routes\n* Real-time stock visibility\n* Structured transfers\n* Lot traceability\n* Exception alerts\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
