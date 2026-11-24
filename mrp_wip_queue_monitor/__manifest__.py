# -*- coding: utf-8 -*-
{
    "name": "Mrp Wip Queue Monitor",
    "version": "20.0.1.0.0",
    "category": "Manufacturing/Manufacturing",
    "summary": "Mrp Wip Queue Monitor keeps production orders, work in progress and queues under control in Odoo, with workflow statuses and exports.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["mrp", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/mrp_wip_queue_monitor_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nMrp Wip Queue Monitor\n=====================\nMrp Wip Queue Monitor keeps production orders, work in progress and queues under control in Odoo, with workflow statuses and exports.\n\nFeatures:\n---------\n* Production orders\n* Work in progress\n* Queues\n* Production planning\n* Work-order control\n* BOM accuracy\n* Cost tracking\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
