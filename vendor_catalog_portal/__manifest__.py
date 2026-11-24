# -*- coding: utf-8 -*-
{
    "name": "Vendor Catalog Portal",
    "version": "20.0.1.0.0",
    "category": "Purchase/Purchase",
    "summary": "Track vendor records, catalog and customer portal in a dedicated Odoo workspace, from intake to reporting.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["purchase", "product", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/vendor_catalog_portal_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nVendor Catalog Portal\n=====================\nTrack vendor records, catalog and customer portal in a dedicated Odoo workspace, from intake to reporting.\n\nFeatures:\n---------\n* Vendor records\n* Catalog\n* Customer portal\n* Supplier records\n* Purchase approvals\n* Cost control\n* Receipt visibility\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
