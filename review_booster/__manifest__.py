# -*- coding: utf-8 -*-
{
    "name": "Review Booster",
    "version": "18.0.1.0.0",
    "summary": "Google review requests with QR link, opt-in proof and click tracking.",
    "description": """
Review Booster
==============
Collect Google reviews on Odoo 18: opt-in proof per customer, automatic
review requests after invoicing or delivery, short redirect links with
click tracking and opt-out handling.
    """,
    "author": "Farid SLIMANI",
    "website": "https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI",
    "category": "Marketing",
    "license": "OPL-1",
    "price": 39.0,
    "currency": "EUR",
    "depends": ["base", "mail", "account", "stock", "website"],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "data/sequence.xml",
        "views/campaign_views.xml",
        "views/request_views.xml",
        "views/partner_views.xml",
        "views/menus.xml",
    ],
    "images": ["static/description/banner.png"],
    "installable": True,
    "application": False,
    "auto_install": False,
}
