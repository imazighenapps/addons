# -*- coding: utf-8 -*-
{
    "name": "Auth Policy Enforcer",
    "version": "20.0.1.0.0",
    "category": "Administration/Administration",
    "summary": "Auth Policy Enforcer gives teams a focused Odoo app for auth, policies and enforcer, with real-time visibility.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["base", "auth_totp", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/auth_policy_enforcer_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nAuth Policy Enforcer\n====================\nAuth Policy Enforcer gives teams a focused Odoo app for auth, policies and enforcer, with real-time visibility.\n\nFeatures:\n---------\n* Auth\n* Policies\n* Enforcer\n* Dedicated workspace\n* Structured records\n* Workflow statuses\n* Role-based access\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
