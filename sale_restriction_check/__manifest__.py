# -*- coding: utf-8 -*-
{
    "name": "Sale Restriction Check",
    "version": "18.0.1.0.0",
    "category": "Sales/Sales",
    "summary": "Centralize sales, restriction and checks in one Odoo workspace, with role-based access and approvals.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["sale", "point_of_sale", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/sale_restriction_check_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nSale Restriction Check\n======================\nCentralize sales, restriction and checks in one Odoo workspace, with role-based access and approvals.\n\nFeatures:\n---------\n* Sales\n* Restriction\n* Checks\n* Pipeline visibility\n* Fast quotations\n* Customer follow-ups\n* Pricing control\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
