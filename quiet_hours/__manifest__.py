# -*- coding: utf-8 -*-
{
    "name": "Quiet Hours",
    "version": "20.0.1.0.0",
    "category": "Productivity/Productivity",
    "summary": "Organize daily work, approvals and documents in a focused Odoo workspace.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/quiet_hours_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
