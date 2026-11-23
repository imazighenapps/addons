# -*- coding: utf-8 -*-
{
    "name": "Poc Revenue Recognition",
    "version": "19.0.1.0.0",
    "category": "Accounting/Accounting",
    "summary": "Run poc and revenue recognition end to end in Odoo, with structured records and audit-ready history.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["account", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/poc_revenue_recognition_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nPoc Revenue Recognition\n=======================\nRun poc and revenue recognition end to end in Odoo, with structured records and audit-ready history.\n\nFeatures:\n---------\n* Poc\n* Revenue recognition\n* Audit-ready entries\n* Variance tracking\n* Reconciliation workspace\n* Role-based access\n* Export-ready reports\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
