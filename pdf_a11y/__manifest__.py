# -*- coding: utf-8 -*-
{
    "name": "Pdf A Y",
    "version": "20.0.1.0.0",
    "category": "Productivity/Productivity",
    "summary": "Organize daily work, approvals and documents in a focused Odoo workspace.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["base", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/pdf_a11y_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
