# -*- coding: utf-8 -*-
{
    "name": "Hr Overtime Rate Table",
    "version": "19.0.1.0.0",
    "category": "Human Resources/Human Resources",
    "summary": "Automate leave, attendance and employee lifecycle processes with full traceability.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["hr", "hr_attendance", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/hr_overtime_rate_table_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
