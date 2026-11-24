# -*- coding: utf-8 -*-
{
    "name": "Garage Labor Catalog",
    "version": "20.0.1.0.0",
    "category": "Productivity/Productivity",
    "summary": "Centralize garage operations, labor and catalog in one Odoo workspace, with role-based access and approvals.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["sale", "account", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/garage_labor_catalog_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nGarage Labor Catalog\n====================\nCentralize garage operations, labor and catalog in one Odoo workspace, with role-based access and approvals.\n\nFeatures:\n---------\n* Garage operations\n* Labor\n* Catalog\n* Dedicated workspace\n* Structured records\n* Workflow statuses\n* Role-based access\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
