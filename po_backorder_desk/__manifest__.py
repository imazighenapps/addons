# -*- coding: utf-8 -*-
{
    "name": "Po Backorder Desk",
    "version": "20.0.1.0.0",
    "category": "Purchase/Purchase",
    "summary": "Po Backorder Desk: manage purchase orders and backorder in Odoo, with clear statuses and full traceability.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["purchase", "stock", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/po_backorder_desk_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nPo Backorder Desk\n=================\nPo Backorder Desk: manage purchase orders and backorder in Odoo, with clear statuses and full traceability.\n\nFeatures:\n---------\n* Purchase orders\n* Backorder\n* Supplier records\n* Purchase approvals\n* Cost control\n* Receipt visibility\n* Vendor comparison\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
