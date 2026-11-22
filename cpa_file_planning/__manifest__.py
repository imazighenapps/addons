# -*- coding: utf-8 -*-
{
    "name": "Cpa File Planning",
    "version": "19.0.1.0.0",
    "category": "Productivity/Productivity",
    "summary": "Organize daily work, approvals and documents in a focused Odoo workspace.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["project", "account", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/cpa_file_planning_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
