# -*- coding: utf-8 -*-
{
    "name": "Event Floor",
    "version": "20.0.1.0.0",
    "category": "Project/Project",
    "summary": "Give service teams a focused Odoo app for planning, execution and billing.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["event", "sale", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/event_floor_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
