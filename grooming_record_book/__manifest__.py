# -*- coding: utf-8 -*-
{
    "name": "Grooming Record Book",
    "version": "18.0.1.0.0",
    "category": "Productivity/Productivity",
    "summary": "Organize daily work, approvals and documents in a focused Odoo workspace.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["sale", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/grooming_record_book_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
