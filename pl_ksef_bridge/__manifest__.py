# -*- coding: utf-8 -*-
{
    "name": "Pl Ksef Bridge",
    "version": "20.0.1.0.0",
    "category": "Accounting",
    "summary": "Manage KSeF e-invoicing and bridge from a single Odoo screen, with filters, follow-ups and reporting.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["account", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/pl_ksef_bridge_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 99.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nPl Ksef Bridge\n==============\nManage KSeF e-invoicing and bridge from a single Odoo screen, with filters, follow-ups and reporting.\n\nFeatures:\n---------\n* KSeF e-invoicing\n* Bridge\n* Audit-ready entries\n* Variance tracking\n* Reconciliation workspace\n* Role-based access\n* Export-ready reports\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
