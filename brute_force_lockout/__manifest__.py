# -*- coding: utf-8 -*-
{
    "name": "Brute Force Lockout",
    "version": "19.0.1.0.0",
    "category": "Administration/Administration",
    "summary": "Extend Odoo safely with a production-ready, well-documented technical module.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["base", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/brute_force_lockout_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
