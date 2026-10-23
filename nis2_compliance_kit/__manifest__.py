# -*- coding: utf-8 -*-
{
    "name": "NIS2 Compliance Kit",
    "version": "19.0.1.0.0",
    "summary": "NIS2 governance toolkit: assets, Article 21 controls, risks, suppliers, 24/72h incident workflow, board reviews.",
    "description": """
NIS2 Compliance Kit
===================
Governance and evidence toolkit for the NIS2 Directive (EU) 2022/2555.
Helps essential and important entities steer their compliance: asset
register, Article 21 controls library, risk register, supplier cyber
reviews, incident notification workflow (early warning 24h, notification
72h, final report 1 month), corrective actions, training register and
management reviews.

This module is a steering aid. It does not grant compliance by itself and
does not file reports with any authority.
    """,
    "author": "Farid SLIMANI",
    "website": "https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI",
    "category": "Industries",
    "license": "OPL-1",
    "price": 149.0,
    "currency": "EUR",
    "depends": ["base", "mail"],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "data/sectors.xml",
        "data/controls.xml",
        "data/sequence.xml",
        "views/profile_views.xml",
        "views/asset_views.xml",
        "views/control_views.xml",
        "views/risk_views.xml",
        "views/supplier_views.xml",
        "views/incident_views.xml",
        "views/evidence_views.xml",
        "views/training_views.xml",
        "views/review_views.xml",
        "views/action_views.xml",
        "views/menus.xml",
    ],
    "images": ["static/description/banner.png"],
    "installable": True,
    "application": True,
    "auto_install": False,
}
