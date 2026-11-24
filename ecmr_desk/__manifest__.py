# -*- coding: utf-8 -*-
{
    "name": "Ecmr Desk",
    "version": "20.0.1.0.0",
    "category": "Inventory/Inventory",
    "summary": "Run ecmr end to end in Odoo, with structured records and audit-ready history.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["stock", "sale", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/ecmr_desk_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nEcmr Desk\n=========\nRun ecmr end to end in Odoo, with structured records and audit-ready history.\n\nFeatures:\n---------\n* Ecmr\n* Dedicated workspace\n* Structured records\n* Workflow statuses\n* Role-based access\n* Grouped views\n* Audit-ready history\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
