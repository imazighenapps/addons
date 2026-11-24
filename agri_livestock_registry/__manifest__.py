# -*- coding: utf-8 -*-
{
    "name": "Agri Livestock Registry",
    "version": "20.0.1.0.0",
    "category": "Productivity/Productivity",
    "summary": "Centralize agriculture, livestock and a central registry in one Odoo workspace, with role-based access and approvals.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["stock", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/agri_livestock_registry_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nAgri Livestock Registry\n=======================\nCentralize agriculture, livestock and a central registry in one Odoo workspace, with role-based access and approvals.\n\nFeatures:\n---------\n* Agriculture\n* Livestock\n* A central registry\n* Real-time stock visibility\n* Structured transfers\n* Lot traceability\n* Exception alerts\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
