# -*- coding: utf-8 -*-
{
    "name": "Discuss SLA & Handover",
    "version": "19.0.1.0.0",
    "summary": "SLA tracking and team handover log for internal helpdesk on Odoo Discuss.",
    "description": """
Discuss SLA & Handover
=====================
Run an internal helpdesk on Odoo 19 Discuss: per-channel SLA targets,
first-response and resolution timers, breach alerts, automatic channel
archival when idle, and a structured shift handover log so nothing falls
between two teams.
    """,
    "author": "Farid SLIMANI",
    "website": "https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI",
    "category": "Discuss",
    "license": "OPL-1",
    "price": 49.0,
    "currency": "EUR",
    "depends": ["base", "mail"],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "data/sequence.xml",
        "views/policy_views.xml",
        "views/case_views.xml",
        "views/handover_views.xml",
        "views/channel_views.xml",
        "views/menus.xml",
    ],
    "images": ["static/description/banner.png"],
    "installable": True,
    "application": False,
    "auto_install": False,
}