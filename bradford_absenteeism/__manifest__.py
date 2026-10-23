# -*- coding: utf-8 -*-
{
    "name": "Bradford Absenteeism HR",
    "version": "18.0.1.0.0",
    "summary": "Bradford Factor absenteeism scoring, thresholds, return-to-work interviews.",
    "description": """
Bradford Absenteeism HR
=======================
Turn validated sick leaves into an actionable presence indicator for Odoo 18:
Bradford Factor (S squared x D) over a rolling 52 weeks, configurable
threshold bands with non-disciplinary alerts, return-to-work interviews and
manager reporting. No diagnosis is ever stored.
    """,
    "author": "Farid SLIMANI",
    "website": "https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI",
    "category": "Human Resources",
    "license": "OPL-1",
    "price": 69.0,
    "currency": "EUR",
    "depends": ["base", "mail", "hr", "hr_holidays"],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "data/thresholds.xml",
        "views/employee_views.xml",
        "views/threshold_views.xml",
        "views/alert_views.xml",
        "views/rtw_views.xml",
        "views/leave_views.xml",
        "views/menus.xml",
    ],
    "images": ["static/description/banner.png"],
    "installable": True,
    "application": False,
    "auto_install": False,
}
