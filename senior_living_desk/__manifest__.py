# -*- coding: utf-8 -*-
{
    "name": "Senior Living Desk",
    "version": "20.0.1.0.0",
    "category": "Productivity/Productivity",
    "summary": "Centralize senior and living in one Odoo workspace, with role-based access and approvals.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["sale", "account", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/senior_living_desk_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nSenior Living Desk\n==================\nCentralize senior and living in one Odoo workspace, with role-based access and approvals.\n\nFeatures:\n---------\n* Senior\n* Living\n* Dedicated workspace\n* Structured records\n* Workflow statuses\n* Role-based access\n* Grouped views\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
