# -*- coding: utf-8 -*-
{
    "name": "Timesheet Gap Watch",
    "version": "20.0.1.0.0",
    "category": "Project/Project",
    "summary": "Run timesheets, gap and monitoring end to end in Odoo, with structured records and audit-ready history.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["hr_timesheet", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/timesheet_gap_watch_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nTimesheet Gap Watch\n===================\nRun timesheets, gap and monitoring end to end in Odoo, with structured records and audit-ready history.\n\nFeatures:\n---------\n* Timesheets\n* Gap\n* Monitoring\n* Project workspace\n* Task tracking\n* Time and billing\n* Milestone planning\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
