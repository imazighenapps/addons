# -*- coding: utf-8 -*-
{
    "name": "Doc Full Text Search",
    "version": "18.0.1.0.0",
    "category": "Productivity/Productivity",
    "summary": "Organize daily work, approvals and documents in a focused Odoo workspace.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["base", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/doc_full_text_search_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
