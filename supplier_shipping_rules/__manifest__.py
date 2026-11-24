# -*- coding: utf-8 -*-
{
    "name": "Supplier Shipping Rules",
    "version": "20.0.1.0.0",
    "category": "Purchase/Purchase",
    "summary": "Manage supplier records, shipping and business rules from a single Odoo screen, with filters, follow-ups and reporting.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["purchase", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/supplier_shipping_rules_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nSupplier Shipping Rules\n=======================\nManage supplier records, shipping and business rules from a single Odoo screen, with filters, follow-ups and reporting.\n\nFeatures:\n---------\n* Supplier records\n* Shipping\n* Business rules\n* Purchase approvals\n* Cost control\n* Receipt visibility\n* Vendor comparison\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
