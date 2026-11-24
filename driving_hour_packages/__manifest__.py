# -*- coding: utf-8 -*-
{
    "name": "Driving Hour Packages",
    "version": "20.0.1.0.0",
    "category": "Productivity/Productivity",
    "summary": "Centralize driving, hourly rates and packages in one Odoo workspace, with role-based access and approvals.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["sale", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/driving_hour_packages_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nDriving Hour Packages\n=====================\nCentralize driving, hourly rates and packages in one Odoo workspace, with role-based access and approvals.\n\nFeatures:\n---------\n* Driving\n* Hourly rates\n* Packages\n* Dedicated workspace\n* Structured records\n* Workflow statuses\n* Role-based access\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
