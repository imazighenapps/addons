# -*- coding: utf-8 -*-
{
    "name": "School Meal Planner",
    "version": "20.0.1.0.0",
    "category": "Productivity/Productivity",
    "summary": "Manage school, meal and planning from a single Odoo screen, with filters, follow-ups and reporting.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["account", "stock", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/school_meal_planner_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nSchool Meal Planner\n===================\nManage school, meal and planning from a single Odoo screen, with filters, follow-ups and reporting.\n\nFeatures:\n---------\n* School\n* Meal\n* Planning\n* Dedicated workspace\n* Structured records\n* Workflow statuses\n* Role-based access\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
