# -*- coding: utf-8 -*-
{
    "name": "Supplier Payment Priority",
    "version": "18.0.1.0.0",
    "category": "Accounting/Accounting",
    "summary": "Centralize supplier records, payments and priority handling in one Odoo workspace, with role-based access and approvals.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["account", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/supplier_payment_priority_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nSupplier Payment Priority\n=========================\nCentralize supplier records, payments and priority handling in one Odoo workspace, with role-based access and approvals.\n\nFeatures:\n---------\n* Supplier records\n* Payments\n* Priority handling\n* Audit-ready entries\n* Variance tracking\n* Reconciliation workspace\n* Role-based access\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
