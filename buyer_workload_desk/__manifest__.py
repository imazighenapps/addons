# -*- coding: utf-8 -*-
{
    "name": "Buyer Workload Desk",
    "version": "20.0.1.0.0",
    "category": "Purchase/Purchase",
    "summary": "Run buyer and workload end to end in Odoo, with structured records and audit-ready history.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["purchase", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/buyer_workload_desk_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nBuyer Workload Desk\n===================\nRun buyer and workload end to end in Odoo, with structured records and audit-ready history.\n\nFeatures:\n---------\n* Buyer\n* Workload\n* Supplier records\n* Purchase approvals\n* Cost control\n* Receipt visibility\n* Vendor comparison\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
