# -*- coding: utf-8 -*-
{
    "name": "Amap Basket Plan",
    "version": "20.0.1.0.0",
    "category": "Productivity/Productivity",
    "summary": "Centralize amap, basket and planning in one Odoo workspace, with role-based access and approvals.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["sale", "stock", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/amap_basket_plan_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nAmap Basket Plan\n================\nCentralize amap, basket and planning in one Odoo workspace, with role-based access and approvals.\n\nFeatures:\n---------\n* Amap\n* Basket\n* Planning\n* Dedicated workspace\n* Structured records\n* Workflow statuses\n* Role-based access\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
