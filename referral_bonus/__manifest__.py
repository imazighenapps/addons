# -*- coding: utf-8 -*-
{
    "name": "Employee Referral Bonus",
    "version": "20.0.1.0.0",
    "summary": "Employee referral programme with hire tracking and bonus payouts.",
    "description": """
Employee Referral Bonus
=======================
Turn employee referrals into a measurable hiring channel: referral campaigns,
candidate pipeline linked to the referrer, automatic tracking from application
to probation pass, and configurable bonus payouts per milestone.
    """,
    "author": "Farid SLIMANI",
    "website": "https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI",
    "category": "Human Resources",
    "license": "OPL-1",
    "price": 39.0,
    "currency": "EUR",
    "depends": ["base", "mail", "hr", "hr_recruitment"],
    "data": [
        "security/security.xml",
        "security/ir.access.csv",
        "data/sequence.xml",
        "views/campaign_views.xml",
        "views/referral_views.xml",
        "views/payout_views.xml",
        "views/menus.xml",
    ],
    "images": ["static/description/banner.png"],
    "installable": True,
    "application": False,
    "auto_install": False,
}