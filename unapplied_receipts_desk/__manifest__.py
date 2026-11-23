# -*- coding: utf-8 -*-
{
    "name": "Unapplied Receipts Desk",
    "version": "18.0.1.0.0",
    "category": "Accounting/Accounting",
    "summary": "Centralize unapplied and receipts in one Odoo workspace, with role-based access and approvals.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["account", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/unapplied_receipts_desk_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nUnapplied Receipts Desk\n=======================\nCentralize unapplied and receipts in one Odoo workspace, with role-based access and approvals.\n\nFeatures:\n---------\n* Unapplied\n* Receipts\n* Audit-ready entries\n* Variance tracking\n* Reconciliation workspace\n* Role-based access\n* Export-ready reports\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
