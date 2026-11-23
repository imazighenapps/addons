# -*- coding: utf-8 -*-
{
    "name": "Optics Lab Orders",
    "version": "20.0.1.0.0",
    "category": "Productivity/Productivity",
    "summary": "Give operations teams a single place to track requests, actions and results.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["purchase", "sale", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/optics_lab_orders_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
