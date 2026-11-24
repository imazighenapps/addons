# -*- coding: utf-8 -*-
{
    "name": "Mx Cfdi Pack",
    "version": "20.0.1.0.0",
    "category": "Accounting",
    "summary": "Track CFDI e-invoicing in a dedicated Odoo workspace, from intake to reporting.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["account", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/mx_cfdi_pack_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 99.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nMx Cfdi Pack\n============\nTrack CFDI e-invoicing in a dedicated Odoo workspace, from intake to reporting.\n\nFeatures:\n---------\n* CFDI e-invoicing\n* Audit-ready entries\n* Variance tracking\n* Reconciliation workspace\n* Role-based access\n* Export-ready reports\n* Multi-company safe\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
