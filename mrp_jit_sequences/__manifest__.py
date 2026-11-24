# -*- coding: utf-8 -*-
{
    "name": "Mrp Jit Sequences",
    "version": "20.0.1.0.0",
    "category": "Manufacturing/Manufacturing",
    "summary": "Track production orders, jit and sequences in a dedicated Odoo workspace, from intake to reporting.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["mrp", "sale", "stock", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/mrp_jit_sequences_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nMrp Jit Sequences\n=================\nTrack production orders, jit and sequences in a dedicated Odoo workspace, from intake to reporting.\n\nFeatures:\n---------\n* Production orders\n* Jit\n* Sequences\n* Production planning\n* Work-order control\n* BOM accuracy\n* Cost tracking\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
