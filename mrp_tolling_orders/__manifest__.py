# -*- coding: utf-8 -*-
{
    "name": "Mrp Tolling Orders",
    "version": "20.0.1.0.0",
    "category": "Manufacturing/Manufacturing",
    "summary": "Mrp Tolling Orders keeps production orders and tolling under control in Odoo, with workflow statuses and exports.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["mrp", "stock", "sale", "purchase", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/mrp_tolling_orders_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nMrp Tolling Orders\n==================\nMrp Tolling Orders keeps production orders and tolling under control in Odoo, with workflow statuses and exports.\n\nFeatures:\n---------\n* Production orders\n* Tolling\n* Production planning\n* Work-order control\n* BOM accuracy\n* Cost tracking\n* Quality checks\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
