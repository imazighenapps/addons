# -*- coding: utf-8 -*-
{
    "name": "Technician Cost Rates",
    "version": "18.0.1.0.0",
    "category": "Project/Project",
    "summary": "Give service teams a focused Odoo app for planning, execution and billing.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["hr_timesheet", "project", "account", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/technician_cost_rates_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
