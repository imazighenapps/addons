# -*- coding: utf-8 -*-
{
    "name": "Tech Performance",
    "version": "18.0.1.0.0",
    "category": "Project/Project",
    "summary": "Give service teams a focused Odoo app for planning, execution and billing.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["project", "hr_timesheet", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/tech_performance_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
