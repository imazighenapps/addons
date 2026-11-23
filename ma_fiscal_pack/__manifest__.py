# -*- coding: utf-8 -*-
{
    "name": "Ma Fiscal Pack",
    "version": "19.0.1.0.0",
    "category": "Accounting",
    "summary": "Run fiscal controls end to end in Odoo, with structured records and audit-ready history.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["account", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/ma_fiscal_pack_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 59.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nMa Fiscal Pack\n==============\nRun fiscal controls end to end in Odoo, with structured records and audit-ready history.\n\nFeatures:\n---------\n* Fiscal controls\n* Audit-ready entries\n* Variance tracking\n* Reconciliation workspace\n* Role-based access\n* Export-ready reports\n* Multi-company safe\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
