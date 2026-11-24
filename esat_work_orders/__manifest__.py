# -*- coding: utf-8 -*-
{
    "name": "Esat Work Orders",
    "version": "20.0.1.0.0",
    "category": "Productivity/Productivity",
    "summary": "Centralize esat, work and orders in one Odoo workspace, with role-based access and approvals.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["mrp", "hr", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/esat_work_orders_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nEsat Work Orders\n================\nCentralize esat, work and orders in one Odoo workspace, with role-based access and approvals.\n\nFeatures:\n---------\n* Esat\n* Work\n* Orders\n* Dedicated workspace\n* Structured records\n* Workflow statuses\n* Role-based access\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
