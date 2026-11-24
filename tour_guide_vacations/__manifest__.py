# -*- coding: utf-8 -*-
{
    "name": "Tour Guide Vacations",
    "version": "20.0.1.0.0",
    "category": "Productivity/Productivity",
    "summary": "Centralize tour, guide and vacations in one Odoo workspace, with role-based access and approvals.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["hr", "sale", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/tour_guide_vacations_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nTour Guide Vacations\n====================\nCentralize tour, guide and vacations in one Odoo workspace, with role-based access and approvals.\n\nFeatures:\n---------\n* Tour\n* Guide\n* Vacations\n* Dedicated workspace\n* Structured records\n* Workflow statuses\n* Role-based access\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
