# -*- coding: utf-8 -*-
{
    "name": "Assoc Volunteer Missions",
    "version": "18.0.1.0.0",
    "category": "Productivity/Productivity",
    "summary": "Organize daily work, approvals and documents in a focused Odoo workspace.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["hr", "calendar", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/assoc_volunteer_missions_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
