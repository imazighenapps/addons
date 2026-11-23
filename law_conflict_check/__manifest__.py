# -*- coding: utf-8 -*-
{
    "name": "Law Conflict Check",
    "version": "20.0.1.0.0",
    "category": "Productivity/Productivity",
    "summary": "Automate repetitive tasks and keep teams aligned with structured Odoo workflows.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["crm", "sale", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/law_conflict_check_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
