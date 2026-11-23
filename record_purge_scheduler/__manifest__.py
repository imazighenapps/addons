# -*- coding: utf-8 -*-
{
    "name": "Record Purge Scheduler",
    "version": "20.0.1.0.0",
    "category": "Administration/Administration",
    "summary": "Give technical teams a focused Odoo tool with clean configuration and auditability.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["base", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/record_purge_scheduler_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
