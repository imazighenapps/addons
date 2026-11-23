# -*- coding: utf-8 -*-
{
    "name": "Hr Seasonal Hiring",
    "version": "20.0.1.0.0",
    "category": "Human Resources/Human Resources",
    "summary": "Automate leave, attendance and employee lifecycle processes with full traceability.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["hr_recruitment", "hr", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/hr_seasonal_hiring_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
