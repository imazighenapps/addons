# -*- coding: utf-8 -*-
{
    "name": "Predictive Maintenance Lite",
    "version": "20.0.1.0.0",
    "summary": "Usage counters, thresholds, health score and preventive requests on top of Odoo Maintenance.",
    "description": """
Predictive Maintenance Lite
===========================
Condition-based maintenance for Odoo 20 Community: multi-unit counters per
equipment (hours, cycles, km), warning/critical thresholds with hysteresis,
transparent 0-100 health score, automatic preventive requests without
duplicates, stale-data alerts and a simple reading API.
    """,
    "author": "Farid SLIMANI",
    "website": "https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI",
    "category": "Industries",
    "license": "OPL-1",
    "price": 79.0,
    "currency": "EUR",
    "depends": ["base", "mail", "maintenance"],
    "data": [
        "security/security.xml",
        "security/ir.access.csv",
        "data/counter_types.xml",
        "views/counter_views.xml",
        "views/reading_views.xml",
        "views/threshold_views.xml",
        "views/alert_views.xml",
        "views/equipment_views.xml",
        "views/menus.xml",
    ],
    "images": ["static/description/banner.png"],
    "installable": True,
    "application": False,
    "auto_install": False,
}
