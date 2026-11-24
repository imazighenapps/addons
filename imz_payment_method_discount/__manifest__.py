# -*- coding: utf-8 -*-
{
    "name": "Payment Method Discount",
    "version": "20.0.1.0.0",
    "category": "Sales/Sales",
    "summary": "Centralize payments, method and discounts in one Odoo workspace, with role-based access and approvals.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["sale", "account", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/payment_method_discount_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nPayment Method Discount\n=======================\nCentralize payments, method and discounts in one Odoo workspace, with role-based access and approvals.\n\nFeatures:\n---------\n* Payments\n* Method\n* Discounts\n* Pipeline visibility\n* Fast quotations\n* Customer follow-ups\n* Pricing control\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
