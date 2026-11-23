# -*- coding: utf-8 -*-
{
    "name": "Fiscal Depreciation Split",
    "version": "19.0.1.0.0",
    "category": "Accounting/Accounting",
    "summary": "Track fiscal controls, depreciation and splits in a dedicated Odoo workspace, from intake to reporting.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["account", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/fiscal_depreciation_split_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 59.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nFiscal Depreciation Split\n=========================\nTrack fiscal controls, depreciation and splits in a dedicated Odoo workspace, from intake to reporting.\n\nFeatures:\n---------\n* Fiscal controls\n* Depreciation\n* Splits\n* Audit-ready entries\n* Variance tracking\n* Reconciliation workspace\n* Role-based access\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
