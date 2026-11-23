# -*- coding: utf-8 -*-
{
    "name": "Hr Parental Leave",
    "version": "18.0.1.0.0",
    "category": "Human Resources/Human Resources",
    "summary": "Centralize employee records, contracts and HR workflows in one secure Odoo app.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["hr", "hr_holidays", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/hr_parental_leave_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
