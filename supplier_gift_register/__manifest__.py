# -*- coding: utf-8 -*-
{
    "name": "Supplier Gift Register",
    "version": "20.0.1.0.0",
    "category": "Purchase/Purchase",
    "summary": "Centralize supplier records, corporate gifts and registers in one Odoo workspace, with role-based access and approvals.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["purchase", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/supplier_gift_register_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nSupplier Gift Register\n======================\nCentralize supplier records, corporate gifts and registers in one Odoo workspace, with role-based access and approvals.\n\nFeatures:\n---------\n* Supplier records\n* Corporate gifts\n* Registers\n* Purchase approvals\n* Cost control\n* Receipt visibility\n* Vendor comparison\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
