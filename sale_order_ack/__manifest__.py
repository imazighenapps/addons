# -*- coding: utf-8 -*-
{
    "name": "Sale Order Ack",
    "version": "19.0.1.0.0",
    "category": "Sales/Sales",
    "summary": "Manage sales, orders and ack from a single Odoo screen, with filters, follow-ups and reporting.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["sale", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/sale_order_ack_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nSale Order Ack\n==============\nManage sales, orders and ack from a single Odoo screen, with filters, follow-ups and reporting.\n\nFeatures:\n---------\n* Sales\n* Orders\n* Ack\n* Pipeline visibility\n* Fast quotations\n* Customer follow-ups\n* Pricing control\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
