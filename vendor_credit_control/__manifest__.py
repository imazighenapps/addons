# -*- coding: utf-8 -*-
{
    "name": "Vendor Credit Control",
    "version": "20.0.1.0.0",
    "category": "Purchase/Purchase",
    "summary": "Run vendor records, credit control and controls end to end in Odoo, with structured records and audit-ready history.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["purchase", "account", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/vendor_credit_control_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nVendor Credit Control\n=====================\nRun vendor records, credit control and controls end to end in Odoo, with structured records and audit-ready history.\n\nFeatures:\n---------\n* Vendor records\n* Credit control\n* Controls\n* Supplier records\n* Purchase approvals\n* Cost control\n* Receipt visibility\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
