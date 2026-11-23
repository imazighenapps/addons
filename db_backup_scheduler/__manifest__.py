# -*- coding: utf-8 -*-
{
    "name": "Db Backup Scheduler",
    "version": "18.0.1.0.0",
    "category": "Administration/Administration",
    "summary": "Give technical teams a focused Odoo tool with clean configuration and auditability.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["base", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/db_backup_scheduler_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
