# -*- coding: utf-8 -*-
{
    "name": "Hr Planned Hours Balance",
    "version": "18.0.1.0.0",
    "category": "Human Resources/Human Resources",
    "summary": "Give HR teams a focused workspace for people data, approvals and reporting.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["hr", "hr_attendance", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/hr_planned_hours_balance_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
