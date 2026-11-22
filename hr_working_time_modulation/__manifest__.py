# -*- coding: utf-8 -*-
{
    "name": "Hr Working Time Modulation",
    "version": "19.0.1.0.0",
    "category": "Human Resources/Human Resources",
    "summary": "Give HR teams a focused workspace for people data, approvals and reporting.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["hr", "hr_attendance", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/hr_working_time_modulation_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
