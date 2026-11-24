# -*- coding: utf-8 -*-
{
    "name": "Guarding Post Billing",
    "version": "20.0.1.0.0",
    "category": "Productivity/Productivity",
    "summary": "Centralize guarding and billing in one Odoo workspace, with role-based access and approvals.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["sale", "account", "hr", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/guarding_post_billing_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nGuarding Post Billing\n=====================\nCentralize guarding and billing in one Odoo workspace, with role-based access and approvals.\n\nFeatures:\n---------\n* Guarding\n* Billing\n* Dedicated workspace\n* Structured records\n* Workflow statuses\n* Role-based access\n* Grouped views\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
