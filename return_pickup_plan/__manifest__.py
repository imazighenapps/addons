# -*- coding: utf-8 -*-
{
    "name": "Return Pickup Plan",
    "version": "20.0.1.0.0",
    "category": "Inventory/Inventory",
    "summary": "Centralize returns, pickups and planning in one Odoo workspace, with role-based access and approvals.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["sale", "stock", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/return_pickup_plan_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nReturn Pickup Plan\n==================\nCentralize returns, pickups and planning in one Odoo workspace, with role-based access and approvals.\n\nFeatures:\n---------\n* Returns\n* Pickups\n* Planning\n* Dedicated workspace\n* Structured records\n* Workflow statuses\n* Role-based access\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
