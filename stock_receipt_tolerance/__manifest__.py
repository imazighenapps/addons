# -*- coding: utf-8 -*-
{
    "name": "Stock Receipt Tolerance",
    "version": "18.0.1.0.0",
    "category": "Inventory/Inventory",
    "summary": "Track stock levels, transfers and replenishment with real-time Odoo visibility.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["stock", "purchase", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/stock_receipt_tolerance_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nStock Receipt Tolerance\n=======================\nTrack stock levels, transfers and replenishment with real-time Odoo visibility.\n\nFeatures:\n---------\n* Stock movements\n* Receipts\n* Tolerance\n* Real-time stock visibility\n* Structured transfers\n* Lot traceability\n* Exception alerts\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
