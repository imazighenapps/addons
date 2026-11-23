# -*- coding: utf-8 -*-
{
    "name": "Vendor Survey Cycle",
    "version": "18.0.1.0.0",
    "category": "Purchase/Purchase",
    "summary": "Automate procurement approvals and vendor follow-ups from one Odoo workspace.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["purchase", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/vendor_survey_cycle_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
