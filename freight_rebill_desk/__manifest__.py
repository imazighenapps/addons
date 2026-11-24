# -*- coding: utf-8 -*-
{
    "name": "Freight Rebill Desk",
    "version": "20.0.1.0.0",
    "category": "Inventory/Inventory",
    "summary": "Freight Rebill Desk keeps freight costs and rebilling under control in Odoo, with workflow statuses and exports.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["sale", "stock", "account", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/freight_rebill_desk_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nFreight Rebill Desk\n===================\nFreight Rebill Desk keeps freight costs and rebilling under control in Odoo, with workflow statuses and exports.\n\nFeatures:\n---------\n* Freight costs\n* Rebilling\n* Dedicated workspace\n* Structured records\n* Workflow statuses\n* Role-based access\n* Grouped views\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
