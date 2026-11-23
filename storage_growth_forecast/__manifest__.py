# -*- coding: utf-8 -*-
{
    "name": "Storage Growth Forecast",
    "version": "20.0.1.0.0",
    "category": "Administration/Administration",
    "summary": "Simplify administration, access control and technical maintenance inside Odoo.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["base", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/storage_growth_forecast_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
