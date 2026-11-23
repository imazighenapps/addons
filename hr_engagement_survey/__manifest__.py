# -*- coding: utf-8 -*-
{
    "name": "Hr Engagement Survey",
    "version": "20.0.1.0.0",
    "category": "Human Resources/Human Resources",
    "summary": "Give HR teams a focused workspace for people data, approvals and reporting.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["hr", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/hr_engagement_survey_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
