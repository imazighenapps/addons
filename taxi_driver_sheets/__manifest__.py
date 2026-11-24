# -*- coding: utf-8 -*-
{
    "name": "Taxi Driver Sheets",
    "version": "20.0.1.0.0",
    "category": "Productivity/Productivity",
    "summary": "Centralize taxi, drivers and sheets in one Odoo workspace, with role-based access and approvals.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["sale", "account", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/taxi_driver_sheets_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nTaxi Driver Sheets\n==================\nCentralize taxi, drivers and sheets in one Odoo workspace, with role-based access and approvals.\n\nFeatures:\n---------\n* Taxi\n* Drivers\n* Sheets\n* Dedicated workspace\n* Structured records\n* Workflow statuses\n* Role-based access\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
