# -*- coding: utf-8 -*-
{
    "name": "Technician Cost Rates",
    "version": "20.0.1.0.0",
    "category": "Project/Project",
    "summary": "Track technician, cost tracking and rates in a dedicated Odoo workspace, from intake to reporting.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["hr_timesheet", "project", "account", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/technician_cost_rates_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nTechnician Cost Rates\n=====================\nTrack technician, cost tracking and rates in a dedicated Odoo workspace, from intake to reporting.\n\nFeatures:\n---------\n* Technician\n* Cost tracking\n* Rates\n* Project workspace\n* Task tracking\n* Time and billing\n* Milestone planning\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
