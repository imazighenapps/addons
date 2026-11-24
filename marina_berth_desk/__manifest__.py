# -*- coding: utf-8 -*-
{
    "name": "Marina Berth Desk",
    "version": "20.0.1.0.0",
    "category": "Productivity/Productivity",
    "summary": "Centralize marina and berth in one Odoo workspace, with role-based access and approvals.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["sale", "account", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/marina_berth_desk_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nMarina Berth Desk\n=================\nCentralize marina and berth in one Odoo workspace, with role-based access and approvals.\n\nFeatures:\n---------\n* Marina\n* Berth\n* Dedicated workspace\n* Structured records\n* Workflow statuses\n* Role-based access\n* Grouped views\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
