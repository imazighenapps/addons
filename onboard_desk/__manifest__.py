# -*- coding: utf-8 -*-
{
    'name': 'OnboardDesk',
    'version': '20.0.1.0.0',
    'summary': 'Run a structured onboarding checklist for every new hire with owners, due dates and visible progress.',
    'description': '''OnboardDesk - Day One, Fully Ready
==================================
Run a structured onboarding checklist for every new hire with owners, due dates and visible progress.

Key points:
* Onboarding tasks tracked in a dedicated register.
* Task owners recorded with clear ownership and dates.
* New hire progress visible so nothing slips through.
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
    'price': 59.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
        'hr',
    ],
    'data': [
        'security/security.xml',
        'security/ir.access.csv',
        'views/onboard_desk_entry_0_views.xml',
        'views/onboard_desk_item_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
