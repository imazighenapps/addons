# -*- coding: utf-8 -*-
{
    "name": "Supplier Statement Recon",
    "version": "18.0.1.0.0",
    "category": "Accounting/Accounting",
    "summary": "Track supplier records, statement and reconciliation in a dedicated Odoo workspace, from intake to reporting.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["account", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/supplier_statement_recon_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nSupplier Statement Recon\n========================\nTrack supplier records, statement and reconciliation in a dedicated Odoo workspace, from intake to reporting.\n\nFeatures:\n---------\n* Supplier records\n* Statement\n* Reconciliation\n* Audit-ready entries\n* Variance tracking\n* Reconciliation workspace\n* Role-based access\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
