# -*- coding: utf-8 -*-
{
    "name": "Cleaning Ops Lite",
    "version": "19.0.1.0.0",
    "summary": "Cleaning sites, recurring visits, agent check-in and per-visit billing.",
    "description": """
Cleaning Ops Lite
================
Run a small cleaning or soft-services company on Odoo 19 Community: customer
sites with floor areas, recurring visit plans, agent check-in and check-out
with proof, quality checklists and billing per visit or per square metre.
    """,
    "author": "Farid SLIMANI",
    "website": "https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI",
    "category": "Industries",
    "license": "OPL-1",
    "price": 99.0,
    "currency": "EUR",
    "depends": ["base", "mail", "uom", "sale"],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "data/sequence.xml",
        "views/site_views.xml",
        "views/plan_views.xml",
        "views/visit_views.xml",
        "views/agent_views.xml",
        "views/menus.xml",
    ],
    "images": ["static/description/banner.png"],
    "installable": True,
    "application": False,
    "auto_install": False,
}