# -*- coding: utf-8 -*-
{
    "name": "Weighbridge Desk",
    "version": "20.0.1.0.0",
    "category": "Inventory/Inventory",
    "summary": "Weighbridge Desk gives teams a focused Odoo app for weighbridge, with real-time visibility.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["stock", "purchase", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/weighbridge_desk_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nWeighbridge Desk\n================\nWeighbridge Desk gives teams a focused Odoo app for weighbridge, with real-time visibility.\n\nFeatures:\n---------\n* Weighbridge\n* Dedicated workspace\n* Structured records\n* Workflow statuses\n* Role-based access\n* Grouped views\n* Audit-ready history\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
