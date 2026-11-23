# -*- coding: utf-8 -*-
{
    "name": "Drone Flight Logbook",
    "version": "19.0.1.0.0",
    "category": "Productivity/Productivity",
    "summary": "Automate repetitive tasks and keep teams aligned with structured Odoo workflows.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["hr", "stock", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/drone_flight_logbook_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
