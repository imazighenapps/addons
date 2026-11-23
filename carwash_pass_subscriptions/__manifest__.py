# -*- coding: utf-8 -*-
{
    "name": "Carwash Pass Subscriptions",
    "version": "19.0.1.0.0",
    "category": "Productivity/Productivity",
    "summary": "Automate repetitive tasks and keep teams aligned with structured Odoo workflows.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["sale", "account", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/carwash_pass_subscriptions_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
