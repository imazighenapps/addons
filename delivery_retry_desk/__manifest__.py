# -*- coding: utf-8 -*-
{
    "name": "Delivery Retry Desk",
    "version": "20.0.1.0.0",
    "category": "Inventory/Inventory",
    "summary": "Manage deliveries and retry from a single Odoo screen, with filters, follow-ups and reporting.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["sale", "stock", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/delivery_retry_desk_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nDelivery Retry Desk\n===================\nManage deliveries and retry from a single Odoo screen, with filters, follow-ups and reporting.\n\nFeatures:\n---------\n* Deliveries\n* Retry\n* Dedicated workspace\n* Structured records\n* Workflow statuses\n* Role-based access\n* Grouped views\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
