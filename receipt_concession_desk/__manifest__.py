# -*- coding: utf-8 -*-
{
    "name": "Receipt Concession Desk",
    "version": "20.0.1.0.0",
    "category": "Purchase/Purchase",
    "summary": "Run receipts and concessions end to end in Odoo, with structured records and audit-ready history.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["stock", "purchase", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/receipt_concession_desk_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nReceipt Concession Desk\n=======================\nRun receipts and concessions end to end in Odoo, with structured records and audit-ready history.\n\nFeatures:\n---------\n* Receipts\n* Concessions\n* Supplier records\n* Purchase approvals\n* Cost control\n* Receipt visibility\n* Vendor comparison\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
