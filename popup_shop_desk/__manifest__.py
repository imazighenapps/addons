# -*- coding: utf-8 -*-
{
    "name": "Popup Shop Desk",
    "version": "20.0.1.0.0",
    "category": "Sales/Sales",
    "summary": "Centralize pop-up shops and shop operations in one Odoo workspace, with role-based access and approvals.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["sale", "stock", "point_of_sale", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/popup_shop_desk_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nPopup Shop Desk\n===============\nCentralize pop-up shops and shop operations in one Odoo workspace, with role-based access and approvals.\n\nFeatures:\n---------\n* Pop-up shops\n* Shop operations\n* Pipeline visibility\n* Fast quotations\n* Customer follow-ups\n* Pricing control\n* Renewal tracking\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
