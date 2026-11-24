# -*- coding: utf-8 -*-
{
    "name": "Contact Order Rights",
    "version": "20.0.1.0.0",
    "category": "Sales/Sales",
    "summary": "Centralize contacts, orders and access rights in one Odoo workspace, with role-based access and approvals.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["sale", "portal", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/contact_order_rights_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nContact Order Rights\n====================\nCentralize contacts, orders and access rights in one Odoo workspace, with role-based access and approvals.\n\nFeatures:\n---------\n* Contacts\n* Orders\n* Access rights\n* Pipeline visibility\n* Fast quotations\n* Customer follow-ups\n* Pricing control\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
