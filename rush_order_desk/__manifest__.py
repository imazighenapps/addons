# -*- coding: utf-8 -*-
{
    "name": "Rush Order Desk",
    "version": "19.0.1.0.0",
    "category": "Sales/Sales",
    "summary": "Centralize rush and orders in one Odoo workspace, with role-based access and approvals.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["sale", "stock", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/rush_order_desk_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nRush Order Desk\n===============\nCentralize rush and orders in one Odoo workspace, with role-based access and approvals.\n\nFeatures:\n---------\n* Rush\n* Orders\n* Pipeline visibility\n* Fast quotations\n* Customer follow-ups\n* Pricing control\n* Renewal tracking\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
