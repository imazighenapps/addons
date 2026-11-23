# -*- coding: utf-8 -*-
{
    "name": "Project Close Checklist",
    "version": "18.0.1.0.0",
    "category": "Project/Project",
    "summary": "Give service teams a focused Odoo app for planning, execution and billing.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["project", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/project_close_checklist_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
