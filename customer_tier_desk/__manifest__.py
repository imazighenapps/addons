# -*- coding: utf-8 -*-
{
    'name': 'TierBook',
    'version': '20.0.1.0.0',
    'summary': 'Classify customers into service tiers with clear benefits and review who should move up or down each quarter.',
    'description': '''TierBook - Tiers That Mean Something
====================================
Classify customers into service tiers with clear benefits and review who should move up or down each quarter.

Key points:
* Customer tiers tracked in a dedicated register.
* Tier benefits recorded with clear ownership and dates.
* Tier moves visible so nothing slips through.
* Draft, confirmed and done states with an audit trail.
* Computed totals and counts kept up to date.
* Active flag to archive records no longer needed.
* Company-aware records for multi-company use.
* Mail chatter for notes and follow-up.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Sales/Sales',
    'license': 'OPL-1',
    'price': 49.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.access.csv',
        'views/customer_tier_entry_0_views.xml',
        'views/customer_tier_item_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
