# -*- coding: utf-8 -*-
{
    "name": "Guarding Post Billing",
    "version": "19.0.1.0.0",
    "category": "Productivity/Productivity",
    "summary": "Give operations teams a single place to track requests, actions and results.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["sale", "account", "hr", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/guarding_post_billing_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
