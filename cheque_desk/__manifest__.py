# -*- coding: utf-8 -*-
{
    "name": "Cheque Desk",
    "version": "19.0.1.0.0",
    "category": "Accounting",
    "summary": "Track cheque in a dedicated Odoo workspace, from intake to reporting.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["account", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/cheque_desk_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nCheque Desk\n===========\nTrack cheque in a dedicated Odoo workspace, from intake to reporting.\n\nFeatures:\n---------\n* Cheque\n* Audit-ready entries\n* Variance tracking\n* Reconciliation workspace\n* Role-based access\n* Export-ready reports\n* Multi-company safe\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
