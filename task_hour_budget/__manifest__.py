# -*- coding: utf-8 -*-
{
    "name": "Task Hour Budget",
    "version": "20.0.1.0.0",
    "category": "Project/Project",
    "summary": "Coordinate teams, milestones and deliverables with clear real-time progress.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["project", "hr_timesheet", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/task_hour_budget_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
