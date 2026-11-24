# -*- coding: utf-8 -*-
{
    "name": "Pt Saft Einvoice",
    "version": "20.0.1.0.0",
    "category": "Accounting",
    "summary": "Pt Saft Einvoice keeps SAFT exports and e-invoicing under control in Odoo, with workflow statuses and exports.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["account", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/pt_saft_einvoice_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 99.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nPt Saft Einvoice\n================\nPt Saft Einvoice keeps SAFT exports and e-invoicing under control in Odoo, with workflow statuses and exports.\n\nFeatures:\n---------\n* SAFT exports\n* E-invoicing\n* Audit-ready entries\n* Variance tracking\n* Reconciliation workspace\n* Role-based access\n* Export-ready reports\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
