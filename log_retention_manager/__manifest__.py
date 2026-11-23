# -*- coding: utf-8 -*-
{
    "name": "Log Retention Manager",
    "version": "20.0.1.0.0",
    "category": "Administration/Administration",
    "summary": "Extend Odoo safely with a production-ready, well-documented technical module.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["base", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/log_retention_manager_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
