# -*- coding: utf-8 -*-
{
    "name": "Mrp Process Recipes",
    "version": "20.0.1.0.0",
    "category": "Manufacturing/Manufacturing",
    "summary": "Centralize production orders, processes and recipes in one Odoo workspace, with role-based access and approvals.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["mrp", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/mrp_process_recipes_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nMrp Process Recipes\n===================\nCentralize production orders, processes and recipes in one Odoo workspace, with role-based access and approvals.\n\nFeatures:\n---------\n* Production orders\n* Processes\n* Recipes\n* Production planning\n* Work-order control\n* BOM accuracy\n* Cost tracking\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
