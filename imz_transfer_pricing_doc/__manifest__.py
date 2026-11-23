# -*- coding: utf-8 -*-
{
    "name": "Transfer Pricing Doc",
    "version": "19.0.1.0.0",
    "category": "Accounting/Accounting",
    "summary": "Manage transfers, pricing and documents from a single Odoo screen, with filters, follow-ups and reporting.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["account", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/transfer_pricing_doc_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nTransfer Pricing Doc\n====================\nManage transfers, pricing and documents from a single Odoo screen, with filters, follow-ups and reporting.\n\nFeatures:\n---------\n* Transfers\n* Pricing\n* Documents\n* Audit-ready entries\n* Variance tracking\n* Reconciliation workspace\n* Role-based access\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
