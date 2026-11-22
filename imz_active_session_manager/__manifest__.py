# -*- coding: utf-8 -*-
{
    "name": "Active Session Manager",
    "version": "18.0.1.0.0",
    "category": "Administration/Administration",
    "summary": "Simplify administration, access control and technical maintenance inside Odoo.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["base", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/active_session_manager_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
