# -*- coding: utf-8 -*-
{
    "name": "Coa Mapper",
    "version": "19.0.1.0.0",
    "category": "Accounting/Accounting",
    "summary": "Manage chart of accounts and mapping from a single Odoo screen, with filters, follow-ups and reporting.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["account", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/coa_mapper_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nCoa Mapper\n==========\nManage chart of accounts and mapping from a single Odoo screen, with filters, follow-ups and reporting.\n\nFeatures:\n---------\n* Chart of accounts\n* Mapping\n* Audit-ready entries\n* Variance tracking\n* Reconciliation workspace\n* Role-based access\n* Export-ready reports\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
