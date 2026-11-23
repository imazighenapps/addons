# -*- coding: utf-8 -*-
{
    "name": "Auth Policy Enforcer",
    "version": "20.0.1.0.0",
    "category": "Administration/Administration",
    "summary": "Simplify administration, access control and technical maintenance inside Odoo.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["base", "auth_totp", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/auth_policy_enforcer_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
