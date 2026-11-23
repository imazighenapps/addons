# -*- coding: utf-8 -*-
{
    "name": "Payment Run Planner",
    "version": "18.0.1.0.0",
    "category": "Accounting/Accounting",
    "summary": "Manage payments, run and planning from a single Odoo screen, with filters, follow-ups and reporting.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["account", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/payment_run_planner_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nPayment Run Planner\n===================\nManage payments, run and planning from a single Odoo screen, with filters, follow-ups and reporting.\n\nFeatures:\n---------\n* Payments\n* Run\n* Planning\n* Audit-ready entries\n* Variance tracking\n* Reconciliation workspace\n* Role-based access\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
