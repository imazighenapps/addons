# -*- coding: utf-8 -*-
{
    "name": "Bank Loan Schedule",
    "version": "18.0.1.0.0",
    "category": "Accounting",
    "summary": "Bank Loan Schedule keeps bank reconciliation, loans and scheduling under control in Odoo, with workflow statuses and exports.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["account", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/bank_loan_schedule_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 59.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nBank Loan Schedule\n==================\nBank Loan Schedule keeps bank reconciliation, loans and scheduling under control in Odoo, with workflow statuses and exports.\n\nFeatures:\n---------\n* Bank reconciliation\n* Loans\n* Scheduling\n* Audit-ready entries\n* Variance tracking\n* Reconciliation workspace\n* Role-based access\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
