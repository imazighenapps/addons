# -*- coding: utf-8 -*-
{
    "name": "Quote To Job",
    "version": "20.0.1.0.0",
    "category": "Project/Project",
    "summary": "Give service teams a focused Odoo app for planning, execution and billing.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["sale", "project", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/quote_to_job_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
