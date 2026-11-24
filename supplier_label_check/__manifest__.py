# -*- coding: utf-8 -*-
{
    "name": "Supplier Label Check",
    "version": "20.0.1.0.0",
    "category": "Purchase/Purchase",
    "summary": "Supplier Label Check keeps supplier records, labels and checks under control in Odoo, with workflow statuses and exports.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["stock", "purchase", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/supplier_label_check_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nSupplier Label Check\n====================\nSupplier Label Check keeps supplier records, labels and checks under control in Odoo, with workflow statuses and exports.\n\nFeatures:\n---------\n* Supplier records\n* Labels\n* Checks\n* Purchase approvals\n* Cost control\n* Receipt visibility\n* Vendor comparison\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
