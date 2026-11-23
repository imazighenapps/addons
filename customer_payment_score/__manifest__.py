# -*- coding: utf-8 -*-
{
    "name": "Customer Payment Score",
    "version": "19.0.1.0.0",
    "category": "Accounting/Accounting",
    "summary": "Give operations teams a clear Odoo workflow for customer follow-ups, payments and scoring, with full traceability.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["account", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/customer_payment_score_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nCustomer Payment Score\n======================\nGive operations teams a clear Odoo workflow for customer follow-ups, payments and scoring, with full traceability.\n\nFeatures:\n---------\n* Customer follow-ups\n* Payments\n* Scoring\n* Audit-ready entries\n* Variance tracking\n* Reconciliation workspace\n* Role-based access\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
