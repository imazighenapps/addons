# -*- coding: utf-8 -*-
{
    "name": "Hr Letter Templates",
    "version": "20.0.1.0.0",
    "category": "Human Resources/Human Resources",
    "summary": "Centralize employee records, contracts and HR workflows in one secure Odoo app.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["hr", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/hr_letter_templates_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
