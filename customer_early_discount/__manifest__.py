# -*- coding: utf-8 -*-
{
    "name": "Customer Early Discount",
    "version": "19.0.1.0.0",
    "category": "Accounting/Accounting",
    "summary": "Track customer follow-ups, early and discounts in a dedicated Odoo workspace, from intake to reporting.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["account", "sale", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/customer_early_discount_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nCustomer Early Discount\n=======================\nTrack customer follow-ups, early and discounts in a dedicated Odoo workspace, from intake to reporting.\n\nFeatures:\n---------\n* Customer follow-ups\n* Early\n* Discounts\n* Audit-ready entries\n* Variance tracking\n* Reconciliation workspace\n* Role-based access\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
