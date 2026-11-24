# -*- coding: utf-8 -*-
{
    "name": "Drone Flight Logbook",
    "version": "20.0.1.0.0",
    "category": "Productivity/Productivity",
    "summary": "Track drone, flight and logbook in a dedicated Odoo workspace, from intake to reporting.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["hr", "stock", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/drone_flight_logbook_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nDrone Flight Logbook\n====================\nTrack drone, flight and logbook in a dedicated Odoo workspace, from intake to reporting.\n\nFeatures:\n---------\n* Drone\n* Flight\n* Logbook\n* Dedicated workspace\n* Structured records\n* Workflow statuses\n* Role-based access\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
