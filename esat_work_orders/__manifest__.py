# -*- coding: utf-8 -*-
{
    "name": "Esat Work Orders",
    "version": "19.0.1.0.0",
    "category": "Productivity/Productivity",
    "summary": "Organize daily work, approvals and documents in a focused Odoo workspace.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["mrp", "hr", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/esat_work_orders_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
