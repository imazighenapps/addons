# -*- coding: utf-8 -*-
{
    "name": "Gr Mydata Einvoice",
    "version": "20.0.1.0.0",
    "category": "Accounting",
    "summary": "Gr Mydata Einvoice keeps mydata and e-invoicing under control in Odoo, with workflow statuses and exports.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["account", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/gr_mydata_einvoice_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 99.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nGr Mydata Einvoice\n==================\nGr Mydata Einvoice keeps mydata and e-invoicing under control in Odoo, with workflow statuses and exports.\n\nFeatures:\n---------\n* Mydata\n* E-invoicing\n* Audit-ready entries\n* Variance tracking\n* Reconciliation workspace\n* Role-based access\n* Export-ready reports\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
