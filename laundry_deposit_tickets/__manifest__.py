# -*- coding: utf-8 -*-
{
    "name": "Laundry Deposit Tickets",
    "version": "18.0.1.0.0",
    "category": "Productivity/Productivity",
    "summary": "Automate repetitive tasks and keep teams aligned with structured Odoo workflows.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["sale", "stock", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/laundry_deposit_tickets_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
