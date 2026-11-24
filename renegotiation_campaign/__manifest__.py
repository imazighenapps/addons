# -*- coding: utf-8 -*-
{
    "name": "Renegotiation Campaign",
    "version": "20.0.1.0.0",
    "category": "Purchase/Purchase",
    "summary": "Centralize renegotiation and campaigns in one Odoo workspace, with role-based access and approvals.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["purchase", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/renegotiation_campaign_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nRenegotiation Campaign\n======================\nCentralize renegotiation and campaigns in one Odoo workspace, with role-based access and approvals.\n\nFeatures:\n---------\n* Renegotiation\n* Campaigns\n* Supplier records\n* Purchase approvals\n* Cost control\n* Receipt visibility\n* Vendor comparison\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
