# -*- coding: utf-8 -*-
{
    "name": "Hr Team Roster Builder",
    "version": "19.0.1.0.0",
    "category": "Human Resources/Human Resources",
    "summary": "Give HR teams a focused workspace for people data, approvals and reporting.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["hr", "hr_attendance", "hr_holidays", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/hr_team_roster_builder_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
