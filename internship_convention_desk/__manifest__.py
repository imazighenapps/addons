# -*- coding: utf-8 -*-
{
    "name": "Internship Convention Desk",
    "version": "20.0.1.0.0",
    "category": "Productivity/Productivity",
    "summary": "Organize daily work, approvals and documents in a focused Odoo workspace.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["hr", "project", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/internship_convention_desk_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
