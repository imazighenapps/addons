# -*- coding: utf-8 -*-
{
    "name": "Timesheet Auto Fill",
    "version": "20.0.1.0.0",
    "category": "Project/Project",
    "summary": "Coordinate teams, milestones and deliverables with clear real-time progress.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["hr_timesheet", "project", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/timesheet_auto_fill_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
