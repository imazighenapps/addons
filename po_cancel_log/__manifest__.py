# -*- coding: utf-8 -*-
{
    "name": "Po Cancel Log",
    "version": "20.0.1.0.0",
    "category": "Purchase/Purchase",
    "summary": "Automate procurement approvals and vendor follow-ups from one Odoo workspace.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["purchase", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/po_cancel_log_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
