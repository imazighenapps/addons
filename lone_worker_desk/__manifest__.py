# -*- coding: utf-8 -*-
{
    'name': 'LoneWatch',
    'version': '20.0.1.0.0',
    'summary': 'Schedule lone-worker shifts with timed check-ins and escalate immediately when a check-in is missed.',
    'description': '''LoneWatch - Alone, Never Unwatched
==================================
Schedule lone-worker shifts with timed check-ins and escalate immediately when a check-in is missed.

Key points:
* Lone shifts tracked in a dedicated register.
* Check-ins recorded with clear ownership and dates.
* Missed check-ins visible so nothing slips through.
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
        'views/lone_worker_entry_0_views.xml',
        'views/lone_worker_item_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
