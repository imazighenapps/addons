# -*- coding: utf-8 -*-
{
    "name": "Coa Lot Desk",
    "version": "20.0.1.0.0",
    "category": "Purchase/Purchase",
    "summary": "Centralize chart of accounts and lot traceability in one Odoo workspace, with role-based access and approvals.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["stock", "purchase", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/coa_lot_desk_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nCoa Lot Desk\n============\nCentralize chart of accounts and lot traceability in one Odoo workspace, with role-based access and approvals.\n\nFeatures:\n---------\n* Chart of accounts\n* Lot traceability\n* Supplier records\n* Purchase approvals\n* Cost control\n* Receipt visibility\n* Vendor comparison\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
