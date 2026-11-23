# -*- coding: utf-8 -*-
{
    "name": "Card Settlement Recon",
    "version": "20.0.1.0.0",
    "category": "Accounting",
    "summary": "Run cards, settlements and reconciliation end to end in Odoo, with structured records and audit-ready history.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["account", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/card_settlement_recon_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nCard Settlement Recon\n=====================\nRun cards, settlements and reconciliation end to end in Odoo, with structured records and audit-ready history.\n\nFeatures:\n---------\n* Cards\n* Settlements\n* Reconciliation\n* Audit-ready entries\n* Variance tracking\n* Reconciliation workspace\n* Role-based access\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
