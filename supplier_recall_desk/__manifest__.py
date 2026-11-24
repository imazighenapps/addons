# -*- coding: utf-8 -*-
{
    "name": "Supplier Recall Desk",
    "version": "20.0.1.0.0",
    "category": "Purchase/Purchase",
    "summary": "Supplier Recall Desk gives teams a focused Odoo app for supplier records and recalls, with real-time visibility.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["stock", "purchase", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/supplier_recall_desk_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nSupplier Recall Desk\n====================\nSupplier Recall Desk gives teams a focused Odoo app for supplier records and recalls, with real-time visibility.\n\nFeatures:\n---------\n* Supplier records\n* Recalls\n* Purchase approvals\n* Cost control\n* Receipt visibility\n* Vendor comparison\n* Procurement history\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
