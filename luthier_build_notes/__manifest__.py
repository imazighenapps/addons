# -*- coding: utf-8 -*-
{
    "name": "Luthier Build Notes",
    "version": "18.0.1.0.0",
    "category": "Productivity/Productivity",
    "summary": "Automate repetitive tasks and keep teams aligned with structured Odoo workflows.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["mrp", "stock", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/luthier_build_notes_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
