# -*- coding: utf-8 -*-
{
    "name": "Installed Base Desk",
    "version": "18.0.1.0.0",
    "category": "Project/Project",
    "summary": "Plan tasks, track time and monitor project profitability from a single Odoo workspace.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["project", "sale", "stock", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/installed_base_desk_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
