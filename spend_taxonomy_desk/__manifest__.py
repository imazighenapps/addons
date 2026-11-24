# -*- coding: utf-8 -*-
{
    "name": "Spend Taxonomy Desk",
    "version": "20.0.1.0.0",
    "category": "Purchase/Purchase",
    "summary": "Run spend and taxonomy end to end in Odoo, with structured records and audit-ready history.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["purchase", "account", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/spend_taxonomy_desk_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nSpend Taxonomy Desk\n===================\nRun spend and taxonomy end to end in Odoo, with structured records and audit-ready history.\n\nFeatures:\n---------\n* Spend\n* Taxonomy\n* Supplier records\n* Purchase approvals\n* Cost control\n* Receipt visibility\n* Vendor comparison\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
