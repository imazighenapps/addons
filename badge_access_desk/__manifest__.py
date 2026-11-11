# -*- coding: utf-8 -*-
{
    'name': 'BadgeDesk',
    'version': '20.0.1.0.0',
    'summary': 'Issue access badges per zone, track who holds which rights and recover badges when roles change.',
    'description': '''BadgeDesk - Access Granted, Access Gone
=======================================
Issue access badges per zone, track who holds which rights and recover badges when roles change.

Key points:
* Badges issued tracked in a dedicated register.
* Access zones recorded with clear ownership and dates.
* Badge returns visible so nothing slips through.
* Draft, confirmed and done states with an audit trail.
* Computed totals and counts kept up to date.
* Active flag to archive records no longer needed.
* Company-aware records for multi-company use.
* Mail chatter for notes and follow-up.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Human Resources/Employee',
    'license': 'OPL-1',
    'price': 49.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
        'hr',
    ],
    'data': [
        'security/security.xml',
        'security/ir.access.csv',
        'views/badge_access_entry_0_views.xml',
        'views/badge_access_item_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
