# -*- coding: utf-8 -*-
{
    "name": "Bill Of Exchange Desk",
    "version": "20.0.1.0.0",
    "category": "Accounting",
    "summary": "Bill Of Exchange Desk: manage bills and exchange in Odoo, with clear statuses and full traceability.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["account", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/bill_of_exchange_desk_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nBill Of Exchange Desk\n=====================\nBill Of Exchange Desk: manage bills and exchange in Odoo, with clear statuses and full traceability.\n\nFeatures:\n---------\n* Bills\n* Exchange\n* Audit-ready entries\n* Variance tracking\n* Reconciliation workspace\n* Role-based access\n* Export-ready reports\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
