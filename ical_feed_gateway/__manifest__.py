# -*- coding: utf-8 -*-
{
    "name": "Ical Feed Gateway",
    "version": "20.0.1.0.0",
    "category": "Administration/Administration",
    "summary": "Ical Feed Gateway keeps ical, feed and gateway under control in Odoo, with workflow statuses and exports.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["calendar", "hr", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/ical_feed_gateway_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nIcal Feed Gateway\n=================\nIcal Feed Gateway keeps ical, feed and gateway under control in Odoo, with workflow statuses and exports.\n\nFeatures:\n---------\n* Ical\n* Feed\n* Gateway\n* Dedicated workspace\n* Structured records\n* Workflow statuses\n* Role-based access\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
