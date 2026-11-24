# -*- coding: utf-8 -*-
{
    "name": "Split Billing Entities",
    "version": "19.0.1.0.0",
    "category": "Sales/Sales",
    "summary": "Centralize splits, billing and entities in one Odoo workspace, with role-based access and approvals.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["sale", "account", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/split_billing_entities_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nSplit Billing Entities\n======================\nCentralize splits, billing and entities in one Odoo workspace, with role-based access and approvals.\n\nFeatures:\n---------\n* Splits\n* Billing\n* Entities\n* Pipeline visibility\n* Fast quotations\n* Customer follow-ups\n* Pricing control\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
