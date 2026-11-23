# -*- coding: utf-8 -*-
{
    "name": "Mrp Wip Queue Monitor",
    "version": "18.0.1.0.0",
    "category": "Manufacturing/Manufacturing",
    "summary": "Plan production, track work orders and control costs across your manufacturing chain.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["mrp", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/mrp_wip_queue_monitor_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
