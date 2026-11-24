# -*- coding: utf-8 -*-
{
    "name": "Sale Penalty Registry",
    "version": "20.0.1.0.0",
    "category": "Manufacturing/Manufacturing",
    "summary": "Sale Penalty Registry keeps sales, penalties and a central registry under control in Odoo, with workflow statuses and exports.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["sale", "account", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/sale_penalty_registry_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nSale Penalty Registry\n=====================\nSale Penalty Registry keeps sales, penalties and a central registry under control in Odoo, with workflow statuses and exports.\n\nFeatures:\n---------\n* Sales\n* Penalties\n* A central registry\n* Pipeline visibility\n* Fast quotations\n* Customer follow-ups\n* Pricing control\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
