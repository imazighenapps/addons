# -*- coding: utf-8 -*-
{
    "name": "Lost Lead Recycler",
    "version": "18.0.1.0.0",
    "summary": "Recycle lost and dormant leads back into nurturing with reassignment.",
    "description": """
Lost Lead Recycler
==================
Stop letting 20-30% of your pipeline rot: automatically detect lost or
dormant leads, bring them back to a nurturing stage, reassign them and
track recycling history on Odoo 18 Community CRM.
    """,
    "author": "Farid SLIMANI",
    "website": "https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI",
    "category": "Marketing",
    "license": "OPL-1",
    "price": 49.0,
    "currency": "EUR",
    "depends": ["base", "mail", "crm"],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "data/cron.xml",
        "views/rule_views.xml",
        "views/lead_views.xml",
        "views/menus.xml",
    ],
    "images": ["static/description/banner.png"],
    "installable": True,
    "application": False,
    "auto_install": False,
}
