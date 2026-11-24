# -*- coding: utf-8 -*-
{
    "name": "Min Commit Vendor Desk",
    "version": "20.0.1.0.0",
    "category": "Purchase/Purchase",
    "summary": "Manage min, commitments and vendor records from a single Odoo screen, with filters, follow-ups and reporting.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["purchase", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/min_commit_vendor_desk_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nMin Commit Vendor Desk\n======================\nManage min, commitments and vendor records from a single Odoo screen, with filters, follow-ups and reporting.\n\nFeatures:\n---------\n* Min\n* Commitments\n* Vendor records\n* Supplier records\n* Purchase approvals\n* Cost control\n* Receipt visibility\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
