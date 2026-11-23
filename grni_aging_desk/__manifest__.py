# -*- coding: utf-8 -*-
{
    "name": "Grni Aging Desk",
    "version": "19.0.1.0.0",
    "category": "Accounting/Accounting",
    "summary": "Run grni and aging balances end to end in Odoo, with structured records and audit-ready history.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["account", "stock", "purchase", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/grni_aging_desk_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nGrni Aging Desk\n===============\nRun grni and aging balances end to end in Odoo, with structured records and audit-ready history.\n\nFeatures:\n---------\n* Grni\n* Aging balances\n* Audit-ready entries\n* Variance tracking\n* Reconciliation workspace\n* Role-based access\n* Export-ready reports\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
