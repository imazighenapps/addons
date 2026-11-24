# -*- coding: utf-8 -*-
{
    "name": "Delivered Uninvoiced Queue",
    "version": "18.0.1.0.0",
    "category": "Sales/Sales",
    "summary": "Centralize delivered, uninvoiced and queues in one Odoo workspace, with role-based access and approvals.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["sale", "account", "stock", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/delivered_uninvoiced_queue_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nDelivered Uninvoiced Queue\n==========================\nCentralize delivered, uninvoiced and queues in one Odoo workspace, with role-based access and approvals.\n\nFeatures:\n---------\n* Delivered\n* Uninvoiced\n* Queues\n* Pipeline visibility\n* Fast quotations\n* Customer follow-ups\n* Pricing control\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
