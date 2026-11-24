# -*- coding: utf-8 -*-
{
    "name": "Urban Access Rules",
    "version": "20.0.1.0.0",
    "category": "Inventory/Inventory",
    "summary": "Centralize urban, access and business rules in one Odoo workspace, with role-based access and approvals.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["stock", "sale", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/urban_access_rules_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nUrban Access Rules\n==================\nCentralize urban, access and business rules in one Odoo workspace, with role-based access and approvals.\n\nFeatures:\n---------\n* Urban\n* Access\n* Business rules\n* Dedicated workspace\n* Structured records\n* Workflow statuses\n* Role-based access\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
