# -*- coding: utf-8 -*-
{
    "name": "Overhead Book",
    "version": "20.0.1.0.0",
    "category": "Project/Project",
    "summary": "Give service teams a focused Odoo app for planning, execution and billing.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["project", "analytic", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/overhead_book_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
