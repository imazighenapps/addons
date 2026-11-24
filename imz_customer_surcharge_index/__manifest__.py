# -*- coding: utf-8 -*-
{
    "name": "Customer Surcharge Index",
    "version": "19.0.1.0.0",
    "category": "Sales/Sales",
    "summary": "Track customer follow-ups, surcharges and indexes in a dedicated Odoo workspace, from intake to reporting.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["sale", "account", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/customer_surcharge_index_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nCustomer Surcharge Index\n========================\nTrack customer follow-ups, surcharges and indexes in a dedicated Odoo workspace, from intake to reporting.\n\nFeatures:\n---------\n* Customer follow-ups\n* Surcharges\n* Indexes\n* Pipeline visibility\n* Fast quotations\n* Pricing control\n* Renewal tracking\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
