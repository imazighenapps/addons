# -*- coding: utf-8 -*-
{
    "name": "EU OSS & Intrastat Tracker",
    "version": "18.0.1.0.0",
    "summary": "Track EU OSS/IOSS thresholds per country and Intrastat declaration readiness.",
    "description": """
EU OSS & Intrastat Tracker
==========================
Stay on top of EU cross-border thresholds: cumulative sales per country
against the OSS (EUR 10,000) and IOSS (EUR 150) limits, automatic scheme
switching warnings, Intrastat arrival/dispatch readiness reports and a
declaration file export.
    """,
    "author": "Farid SLIMANI",
    "website": "https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI",
    "category": "Localization",
    "license": "OPL-1",
    "price": 89.0,
    "currency": "EUR",
    "depends": ["base", "mail", "account"],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "data/thresholds.xml",
        "data/sequence.xml",
        "views/threshold_views.xml",
        "views/counter_views.xml",
        "views/intrastat_views.xml",
        "views/wizard_views.xml",
        "views/menus.xml",
    ],
    "images": ["static/description/banner.png"],
    "installable": True,
    "application": False,
    "auto_install": False,
}