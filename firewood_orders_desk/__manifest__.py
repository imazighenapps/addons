# -*- coding: utf-8 -*-
{
    "name": "Firewood Orders Desk",
    "version": "20.0.1.0.0",
    "category": "Productivity/Productivity",
    "summary": "Firewood Orders Desk keeps firewood and orders under control in Odoo, with workflow statuses and exports.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["sale", "stock", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/firewood_orders_desk_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nFirewood Orders Desk\n====================\nFirewood Orders Desk keeps firewood and orders under control in Odoo, with workflow statuses and exports.\n\nFeatures:\n---------\n* Firewood\n* Orders\n* Dedicated workspace\n* Structured records\n* Workflow statuses\n* Role-based access\n* Grouped views\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
