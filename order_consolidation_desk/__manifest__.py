# -*- coding: utf-8 -*-
{
    "name": "Order Consolidation Desk",
    "version": "20.0.1.0.0",
    "category": "Purchase/Purchase",
    "summary": "Order Consolidation Desk gives teams a focused Odoo app for orders and consolidation, with real-time visibility.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["purchase", "stock", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/order_consolidation_desk_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nOrder Consolidation Desk\n========================\nOrder Consolidation Desk gives teams a focused Odoo app for orders and consolidation, with real-time visibility.\n\nFeatures:\n---------\n* Orders\n* Consolidation\n* Supplier records\n* Purchase approvals\n* Cost control\n* Receipt visibility\n* Vendor comparison\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
