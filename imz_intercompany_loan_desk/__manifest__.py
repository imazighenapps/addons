# -*- coding: utf-8 -*-
{
    "name": "Intercompany Loan Desk",
    "version": "20.0.1.0.0",
    "category": "Accounting",
    "summary": "Centralize intercompany flows and loans in one Odoo workspace, with role-based access and approvals.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["account", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/intercompany_loan_desk_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nIntercompany Loan Desk\n======================\nCentralize intercompany flows and loans in one Odoo workspace, with role-based access and approvals.\n\nFeatures:\n---------\n* Intercompany flows\n* Loans\n* Audit-ready entries\n* Variance tracking\n* Reconciliation workspace\n* Role-based access\n* Export-ready reports\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
