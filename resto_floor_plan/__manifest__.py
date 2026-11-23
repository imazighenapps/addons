# -*- coding: utf-8 -*-
{
    "name": "Resto Floor Plan",
    "version": "19.0.1.0.0",
    "category": "Productivity/Productivity",
    "summary": "Organize daily work, approvals and documents in a focused Odoo workspace.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["point_of_sale", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/resto_floor_plan_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
