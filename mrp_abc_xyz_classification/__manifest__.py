# -*- coding: utf-8 -*-
{
    "name": "Mrp Abc Xyz Classification",
    "version": "20.0.1.0.0",
    "category": "Manufacturing/Manufacturing",
    "summary": "Track production orders, abc and xyz in a dedicated Odoo workspace, from intake to reporting.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["mrp", "stock", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/mrp_abc_xyz_classification_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nMrp Abc Xyz Classification\n==========================\nTrack production orders, abc and xyz in a dedicated Odoo workspace, from intake to reporting.\n\nFeatures:\n---------\n* Production orders\n* Abc\n* Xyz\n* Production planning\n* Work-order control\n* BOM accuracy\n* Cost tracking\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
