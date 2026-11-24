# -*- coding: utf-8 -*-
{
    "name": "Receipt Variance Desk",
    "version": "20.0.1.0.0",
    "category": "Purchase/Purchase",
    "summary": "Receipt Variance Desk keeps receipts and variances under control in Odoo, with workflow statuses and exports.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["stock", "purchase", "account", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/receipt_variance_desk_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nReceipt Variance Desk\n=====================\nReceipt Variance Desk keeps receipts and variances under control in Odoo, with workflow statuses and exports.\n\nFeatures:\n---------\n* Receipts\n* Variances\n* Supplier records\n* Purchase approvals\n* Cost control\n* Receipt visibility\n* Vendor comparison\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
