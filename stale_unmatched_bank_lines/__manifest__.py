# -*- coding: utf-8 -*-
{
    "name": "Stale Unmatched Bank Lines",
    "version": "18.0.1.0.0",
    "category": "Accounting/Accounting",
    "summary": "Centralize stale, unmatched and bank reconciliation in one Odoo workspace, with role-based access and approvals.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["account", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/stale_unmatched_bank_lines_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nStale Unmatched Bank Lines\n==========================\nCentralize stale, unmatched and bank reconciliation in one Odoo workspace, with role-based access and approvals.\n\nFeatures:\n---------\n* Stale\n* Unmatched\n* Bank reconciliation\n* Audit-ready entries\n* Variance tracking\n* Reconciliation workspace\n* Role-based access\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
