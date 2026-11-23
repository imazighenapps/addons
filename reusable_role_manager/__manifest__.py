# -*- coding: utf-8 -*-
{
    "name": "Reusable Role Manager",
    "version": "20.0.1.0.0",
    "category": "Administration/Administration",
    "summary": "Give technical teams a focused Odoo tool with clean configuration and auditability.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["base", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/reusable_role_manager_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
