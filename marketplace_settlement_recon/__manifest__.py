# -*- coding: utf-8 -*-
{
    "name": "Marketplace Settlement Recon",
    "version": "19.0.1.0.0",
    "category": "Accounting",
    "summary": "Centralize marketplace, settlements and reconciliation in one Odoo workspace, with role-based access and approvals.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["account", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/marketplace_settlement_recon_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nMarketplace Settlement Recon\n============================\nCentralize marketplace, settlements and reconciliation in one Odoo workspace, with role-based access and approvals.\n\nFeatures:\n---------\n* Marketplace\n* Settlements\n* Reconciliation\n* Audit-ready entries\n* Variance tracking\n* Reconciliation workspace\n* Role-based access\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
