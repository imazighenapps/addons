# -*- coding: utf-8 -*-
{
    "name": "Supplier Edi Desk",
    "version": "20.0.1.0.0",
    "category": "Purchase/Purchase",
    "summary": "Manage supplier records and edi from a single Odoo screen, with filters, follow-ups and reporting.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["purchase", "account", "stock", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/supplier_edi_desk_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nSupplier Edi Desk\n=================\nManage supplier records and edi from a single Odoo screen, with filters, follow-ups and reporting.\n\nFeatures:\n---------\n* Supplier records\n* Edi\n* Purchase approvals\n* Cost control\n* Receipt visibility\n* Vendor comparison\n* Procurement history\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
