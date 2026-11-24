# -*- coding: utf-8 -*-
{
    "name": "Eoq Advisor",
    "version": "20.0.1.0.0",
    "category": "Purchase/Purchase",
    "summary": "Run eoq and advisory end to end in Odoo, with structured records and audit-ready history.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["stock", "purchase", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/eoq_advisor_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nEoq Advisor\n===========\nRun eoq and advisory end to end in Odoo, with structured records and audit-ready history.\n\nFeatures:\n---------\n* Eoq\n* Advisory\n* Supplier records\n* Purchase approvals\n* Cost control\n* Receipt visibility\n* Vendor comparison\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
