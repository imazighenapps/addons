# -*- coding: utf-8 -*-
{
    "name": "GDPR SME Pack",
    "version": "18.0.1.0.0",
    "summary": "GDPR accountability for SMEs: Art.30 register, DSAR workflow, DPIA, 72h breaches.",
    "description": """
GDPR SME Pack
=============
Accountability toolkit for EU SMEs under GDPR: processing register
(Art.30), data subject requests with 1-month SLA (Art.12-22), DPIA
screening (Art.35), breach register with 72h notification workflow
(Art.33-34) and anonymization log with retention rules.
    """,
    "author": "Farid SLIMANI",
    "website": "https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI",
    "category": "Industries",
    "license": "OPL-1",
    "price": 89.0,
    "currency": "EUR",
    "depends": ["base", "mail"],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "data/sequence.xml",
        "views/activity_views.xml",
        "views/dsar_views.xml",
        "views/dpia_views.xml",
        "views/breach_views.xml",
        "views/anonym_views.xml",
        "views/menus.xml",
    ],
    "images": ["static/description/banner.png"],
    "installable": True,
    "application": True,
    "auto_install": False,
}
