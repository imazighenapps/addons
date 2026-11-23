# -*- coding: utf-8 -*-
{
    "name": "Ical Feed Gateway",
    "version": "19.0.1.0.0",
    "category": "Administration/Administration",
    "summary": "Simplify administration, access control and technical maintenance inside Odoo.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["calendar", "hr", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/ical_feed_gateway_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
