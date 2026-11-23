# -*- coding: utf-8 -*-
{
    "name": "Form Spam Guard",
    "version": "18.0.1.0.0",
    "category": "Productivity/Productivity",
    "summary": "Organize daily work, approvals and documents in a focused Odoo workspace.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["website", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/form_spam_guard_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
