# -*- coding: utf-8 -*-
{
    "name": "Popup Shop Desk",
    "version": "19.0.1.0.0",
    "category": "Sales/Sales",
    "summary": "Give sales teams a focused Odoo app to convert opportunities into recurring revenue.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["sale", "stock", "point_of_sale", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/popup_shop_desk_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
