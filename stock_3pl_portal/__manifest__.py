# -*- coding: utf-8 -*-
{
    "name": "Stock 3pl Portal",
    "version": "20.0.1.0.0",
    "category": "Inventory/Inventory",
    "summary": "Give logistics teams a focused Odoo app for faster, error-free stock movements.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["stock", "portal", "sale", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/stock_3pl_portal_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nStock 3pl Portal\n================\nGive logistics teams a focused Odoo app for faster, error-free stock movements.\n\nFeatures:\n---------\n* Stock movements\n* 3PL operations\n* Customer portal\n* Real-time stock visibility\n* Structured transfers\n* Lot traceability\n* Exception alerts\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
