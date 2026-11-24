# -*- coding: utf-8 -*-
{
    "name": "Billing Schedule",
    "version": "20.0.1.0.0",
    "category": "Project/Project",
    "summary": "Billing Schedule keeps billing and scheduling under control in Odoo, with workflow statuses and exports.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["sale", "project", "account", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/billing_schedule_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nBilling Schedule\n================\nBilling Schedule keeps billing and scheduling under control in Odoo, with workflow statuses and exports.\n\nFeatures:\n---------\n* Billing\n* Scheduling\n* Project workspace\n* Task tracking\n* Time and billing\n* Milestone planning\n* Team coordination\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
