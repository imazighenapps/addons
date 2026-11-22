# -*- coding: utf-8 -*-
{
    "name": "Fuel Fleet Cards",
    "version": "18.0.1.0.0",
    "category": "Productivity/Productivity",
    "summary": "Give operations teams a single place to track requests, actions and results.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["account", "purchase", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/fuel_fleet_cards_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
