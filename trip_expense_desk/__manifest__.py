# -*- coding: utf-8 -*-
{
    "name": "Trip Expense Desk",
    "version": "20.0.1.0.0",
    "category": "Inventory/Inventory",
    "summary": "Trip Expense Desk: manage trips and expenses in Odoo, with clear statuses and full traceability.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["hr", "fleet", "account", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/trip_expense_desk_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nTrip Expense Desk\n=================\nTrip Expense Desk: manage trips and expenses in Odoo, with clear statuses and full traceability.\n\nFeatures:\n---------\n* Trips\n* Expenses\n* Dedicated workspace\n* Structured records\n* Workflow statuses\n* Role-based access\n* Grouped views\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
