# -*- coding: utf-8 -*-
{
    "name": "Multi Entity Close Desk",
    "version": "19.0.1.0.0",
    "category": "Accounting/Accounting",
    "summary": "Give finance teams a focused Odoo app for reconciliation, analysis and compliant reporting.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["account", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/multi_entity_close_desk_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
