# -*- coding: utf-8 -*-
{
    "name": "Attachment Delete Guard",
    "version": "20.0.1.0.0",
    "category": "Productivity/Productivity",
    "summary": "Organize daily work, approvals and documents in a focused Odoo workspace.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/attachment_delete_guard_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
