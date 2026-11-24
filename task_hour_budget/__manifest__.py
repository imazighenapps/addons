# -*- coding: utf-8 -*-
{
    "name": "Task Hour Budget",
    "version": "20.0.1.0.0",
    "category": "Project/Project",
    "summary": "Manage tasks, hourly rates and budgets from a single Odoo screen, with filters, follow-ups and reporting.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["project", "hr_timesheet", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/task_hour_budget_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nTask Hour Budget\n================\nManage tasks, hourly rates and budgets from a single Odoo screen, with filters, follow-ups and reporting.\n\nFeatures:\n---------\n* Tasks\n* Hourly rates\n* Budgets\n* Project workspace\n* Task tracking\n* Time and billing\n* Milestone planning\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
