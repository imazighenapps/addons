# -*- coding: utf-8 -*-
{
    "name": "Quote Acceptance Portal",
    "version": "19.0.1.0.0",
    "category": "Sales/Sales",
    "summary": "Centralize quotations, acceptance and customer portal in one Odoo workspace, with role-based access and approvals.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["sale", "portal", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/quote_acceptance_portal_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nQuote Acceptance Portal\n=======================\nCentralize quotations, acceptance and customer portal in one Odoo workspace, with role-based access and approvals.\n\nFeatures:\n---------\n* Quotations\n* Acceptance\n* Customer portal\n* Pipeline visibility\n* Fast quotations\n* Customer follow-ups\n* Pricing control\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
