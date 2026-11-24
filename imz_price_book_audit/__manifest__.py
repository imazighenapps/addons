# -*- coding: utf-8 -*-
{
    "name": "Price Book Audit",
    "version": "20.0.1.0.0",
    "category": "Sales/Sales",
    "summary": "Price Book Audit: manage pricing, bookings and audit trails in Odoo, with clear statuses and full traceability.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["sale", "product", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/price_book_audit_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 59.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nPrice Book Audit\n================\nPrice Book Audit: manage pricing, bookings and audit trails in Odoo, with clear statuses and full traceability.\n\nFeatures:\n---------\n* Pricing\n* Bookings\n* Audit trails\n* Pipeline visibility\n* Fast quotations\n* Customer follow-ups\n* Pricing control\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
