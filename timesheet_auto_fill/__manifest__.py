# -*- coding: utf-8 -*-
{
    "name": "Timesheet Auto Fill",
    "version": "20.0.1.0.0",
    "category": "Project/Project",
    "summary": "Track timesheets and fill in a dedicated Odoo workspace, from intake to reporting.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["hr_timesheet", "project", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/timesheet_auto_fill_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nTimesheet Auto Fill\n===================\nTrack timesheets and fill in a dedicated Odoo workspace, from intake to reporting.\n\nFeatures:\n---------\n* Timesheets\n* Fill\n* Project workspace\n* Task tracking\n* Time and billing\n* Milestone planning\n* Team coordination\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
