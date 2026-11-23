# -*- coding: utf-8 -*-
{
    "name": "Pharma Rx Queue",
    "version": "18.0.1.0.0",
    "category": "Productivity/Productivity",
    "summary": "Give operations teams a single place to track requests, actions and results.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["sale", "stock", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/pharma_rx_queue_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
