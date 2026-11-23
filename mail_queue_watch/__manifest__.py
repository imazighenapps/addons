# -*- coding: utf-8 -*-
{
    "name": "Mail Queue Watch",
    "version": "19.0.1.0.0",
    "category": "Productivity/Productivity",
    "summary": "Give operations teams a single place to track requests, actions and results.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/mail_queue_watch_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
