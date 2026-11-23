# -*- coding: utf-8 -*-
{
    "name": "School Meal Planner",
    "version": "19.0.1.0.0",
    "category": "Productivity/Productivity",
    "summary": "Automate repetitive tasks and keep teams aligned with structured Odoo workflows.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["account", "stock", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/school_meal_planner_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
