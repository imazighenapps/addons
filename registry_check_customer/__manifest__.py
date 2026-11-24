# -*- coding: utf-8 -*-
{
    "name": "Registry Check Customer",
    "version": "19.0.1.0.0",
    "category": "Sales/Sales",
    "summary": "Track a central registry, checks and customer follow-ups in a dedicated Odoo workspace, from intake to reporting.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["crm", "account", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/registry_check_customer_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nRegistry Check Customer\n=======================\nTrack a central registry, checks and customer follow-ups in a dedicated Odoo workspace, from intake to reporting.\n\nFeatures:\n---------\n* A central registry\n* Checks\n* Customer follow-ups\n* Pipeline visibility\n* Fast quotations\n* Pricing control\n* Renewal tracking\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
