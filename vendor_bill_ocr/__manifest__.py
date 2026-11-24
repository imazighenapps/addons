# -*- coding: utf-8 -*-
{
    "name": "Vendor Bill Ocr",
    "version": "20.0.1.0.0",
    "category": "Accounting/Accounting",
    "summary": "Run vendor records, bills and OCR end to end in Odoo, with structured records and audit-ready history.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["account", "purchase", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/vendor_bill_ocr_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nVendor Bill Ocr\n===============\nRun vendor records, bills and OCR end to end in Odoo, with structured records and audit-ready history.\n\nFeatures:\n---------\n* Vendor records\n* Bills\n* OCR\n* Audit-ready entries\n* Variance tracking\n* Reconciliation workspace\n* Role-based access\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
