# -*- coding: utf-8 -*-
{
    "name": "Quote Shipping Estimate",
    "version": "18.0.1.0.0",
    "category": "Sales/Sales",
    "summary": "Give operations teams a clear Odoo workflow for quotations, shipping and estimates, with full traceability.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["sale", "stock", "product", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/quote_shipping_estimate_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nQuote Shipping Estimate\n=======================\nGive operations teams a clear Odoo workflow for quotations, shipping and estimates, with full traceability.\n\nFeatures:\n---------\n* Quotations\n* Shipping\n* Estimates\n* Pipeline visibility\n* Fast quotations\n* Customer follow-ups\n* Pricing control\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
