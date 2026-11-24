# -*- coding: utf-8 -*-
{
    "name": "Self Billing Purchase",
    "version": "20.0.1.0.0",
    "category": "Purchase/Purchase",
    "summary": "Self Billing Purchase keeps billing and purchasing under control in Odoo, with workflow statuses and exports.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["purchase", "stock", "account", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/self_billing_purchase_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nSelf Billing Purchase\n=====================\nSelf Billing Purchase keeps billing and purchasing under control in Odoo, with workflow statuses and exports.\n\nFeatures:\n---------\n* Billing\n* Purchasing\n* Supplier records\n* Purchase approvals\n* Cost control\n* Receipt visibility\n* Vendor comparison\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
