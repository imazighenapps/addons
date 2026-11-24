# -*- coding: utf-8 -*-
{
    "name": "Cargo Insurance Desk",
    "version": "20.0.1.0.0",
    "category": "Inventory/Inventory",
    "summary": "Cargo Insurance Desk gives teams a focused Odoo app for cargo and insurance, with real-time visibility.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["sale", "stock", "account", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/cargo_insurance_desk_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nCargo Insurance Desk\n====================\nCargo Insurance Desk gives teams a focused Odoo app for cargo and insurance, with real-time visibility.\n\nFeatures:\n---------\n* Cargo\n* Insurance\n* Dedicated workspace\n* Structured records\n* Workflow statuses\n* Role-based access\n* Grouped views\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
