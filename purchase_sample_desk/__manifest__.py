# -*- coding: utf-8 -*-
{
    "name": "Purchase Sample Desk",
    "version": "18.0.1.0.0",
    "category": "Purchase/Purchase",
    "summary": "Automate procurement approvals and vendor follow-ups from one Odoo workspace.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["purchase", "stock", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/purchase_sample_desk_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
