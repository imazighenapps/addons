# -*- coding: utf-8 -*-
{
    "name": "Data Import Playbook",
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
        "views/data_import_playbook_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
