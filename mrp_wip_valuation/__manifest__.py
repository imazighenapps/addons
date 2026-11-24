# -*- coding: utf-8 -*-
{
    "name": "Mrp Wip Valuation",
    "version": "20.0.1.0.0",
    "category": "Manufacturing/Manufacturing",
    "summary": "Track production orders, work in progress and valuation in a dedicated Odoo workspace, from intake to reporting.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["mrp", "stock", "account", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/mrp_wip_valuation_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nMrp Wip Valuation\n=================\nTrack production orders, work in progress and valuation in a dedicated Odoo workspace, from intake to reporting.\n\nFeatures:\n---------\n* Production orders\n* Work in progress\n* Valuation\n* Production planning\n* Work-order control\n* BOM accuracy\n* Cost tracking\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
