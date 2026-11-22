# -*- coding: utf-8 -*-
{
    "name": "Dog Boarding Desk",
    "version": "19.0.1.0.0",
    "category": "Productivity/Productivity",
    "summary": "Organize daily work, approvals and documents in a focused Odoo workspace.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["sale", "stock", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/dog_boarding_desk_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
