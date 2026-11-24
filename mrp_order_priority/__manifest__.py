# -*- coding: utf-8 -*-
{
    "name": "Mrp Order Priority",
    "version": "20.0.1.0.0",
    "category": "Manufacturing/Manufacturing",
    "summary": "Centralize production orders and priority handling in one Odoo workspace, with role-based access and approvals.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["mrp", "sale", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/mrp_order_priority_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nMrp Order Priority\n==================\nCentralize production orders and priority handling in one Odoo workspace, with role-based access and approvals.\n\nFeatures:\n---------\n* Production orders\n* Priority handling\n* Production planning\n* Work-order control\n* BOM accuracy\n* Cost tracking\n* Quality checks\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
