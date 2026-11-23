# -*- coding: utf-8 -*-
{
    "name": "Cogs Invoice Engine",
    "version": "19.0.1.0.0",
    "category": "Accounting/Accounting",
    "summary": "Run cogs, invoices and rules engine end to end in Odoo, with structured records and audit-ready history.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["account", "stock", "sale", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/cogs_invoice_engine_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nCogs Invoice Engine\n===================\nRun cogs, invoices and rules engine end to end in Odoo, with structured records and audit-ready history.\n\nFeatures:\n---------\n* Cogs\n* Invoices\n* Rules engine\n* Audit-ready entries\n* Variance tracking\n* Reconciliation workspace\n* Role-based access\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
