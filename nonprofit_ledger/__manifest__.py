# -*- coding: utf-8 -*-
{
    "name": "Nonprofit Ledger",
    "version": "20.0.1.0.0",
    "category": "Accounting/Accounting",
    "summary": "Manage nonprofit and ledger from a single Odoo screen, with filters, follow-ups and reporting.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["account", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/nonprofit_ledger_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nNonprofit Ledger\n================\nManage nonprofit and ledger from a single Odoo screen, with filters, follow-ups and reporting.\n\nFeatures:\n---------\n* Nonprofit\n* Ledger\n* Audit-ready entries\n* Variance tracking\n* Reconciliation workspace\n* Role-based access\n* Export-ready reports\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
