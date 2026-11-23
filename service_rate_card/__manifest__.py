# -*- coding: utf-8 -*-
{
    "name": "Service Rate Card",
    "version": "19.0.1.0.0",
    "category": "Project/Project",
    "summary": "Give service teams a focused Odoo app for planning, execution and billing.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["sale", "project", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/service_rate_card_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
