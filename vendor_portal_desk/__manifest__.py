# -*- coding: utf-8 -*-
{
    "name": "Vendor Portal Desk",
    "version": "20.0.1.0.0",
    "category": "Purchase/Purchase",
    "summary": "Vendor Portal Desk: manage vendor records and customer portal in Odoo, with clear statuses and full traceability.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["purchase", "account", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/vendor_portal_desk_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nVendor Portal Desk\n==================\nVendor Portal Desk: manage vendor records and customer portal in Odoo, with clear statuses and full traceability.\n\nFeatures:\n---------\n* Vendor records\n* Customer portal\n* Supplier records\n* Purchase approvals\n* Cost control\n* Receipt visibility\n* Vendor comparison\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
