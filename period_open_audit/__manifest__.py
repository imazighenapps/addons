# -*- coding: utf-8 -*-
{
    "name": "Period Open Audit",
    "version": "20.0.1.0.0",
    "category": "Accounting/Accounting",
    "summary": "Track period, open balances and audit trails in a dedicated Odoo workspace, from intake to reporting.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["account", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/period_open_audit_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 59.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nPeriod Open Audit\n=================\nTrack period, open balances and audit trails in a dedicated Odoo workspace, from intake to reporting.\n\nFeatures:\n---------\n* Period\n* Open balances\n* Audit trails\n* Audit-ready entries\n* Variance tracking\n* Reconciliation workspace\n* Role-based access\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
