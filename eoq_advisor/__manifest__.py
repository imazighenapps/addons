# -*- coding: utf-8 -*-
{
    "name": "Eoq Advisor",
    "version": "19.0.1.0.0",
    "category": "Purchase/Purchase",
    "summary": "Automate procurement approvals and vendor follow-ups from one Odoo workspace.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["stock", "purchase", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/eoq_advisor_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
