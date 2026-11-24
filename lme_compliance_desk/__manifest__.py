# -*- coding: utf-8 -*-
{
    "name": "Lme Compliance Desk",
    "version": "20.0.1.0.0",
    "category": "Purchase/Purchase",
    "summary": "Centralize lme and compliance checks in one Odoo workspace, with role-based access and approvals.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["account", "purchase", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/lme_compliance_desk_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 59.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nLme Compliance Desk\n===================\nCentralize lme and compliance checks in one Odoo workspace, with role-based access and approvals.\n\nFeatures:\n---------\n* Lme\n* Compliance checks\n* Supplier records\n* Purchase approvals\n* Cost control\n* Receipt visibility\n* Vendor comparison\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
