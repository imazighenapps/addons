# -*- coding: utf-8 -*-
{
    "name": "Mandatory Addon Sale",
    "version": "18.0.1.0.0",
    "category": "Sales/Sales",
    "summary": "Centralize mandatory, addon and sales in one Odoo workspace, with role-based access and approvals.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["sale", "product", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/mandatory_addon_sale_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nMandatory Addon Sale\n====================\nCentralize mandatory, addon and sales in one Odoo workspace, with role-based access and approvals.\n\nFeatures:\n---------\n* Mandatory\n* Addon\n* Sales\n* Pipeline visibility\n* Fast quotations\n* Customer follow-ups\n* Pricing control\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
