# -*- coding: utf-8 -*-
{
    'name': 'OffboardDesk',
    'version': '20.0.1.0.0',
    'summary': 'Run offboarding checklists so equipment, access and final steps are never missed when someone leaves.',
    'description': '''OffboardDesk - Exits Without Loose Ends
=======================================
Run offboarding checklists so equipment, access and final steps are never missed when someone leaves.

Key points:
* Offboarding tasks tracked in a dedicated register.
* Asset returns recorded with clear ownership and dates.
* Access revocations visible so nothing slips through.
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
        'views/offboard_desk_entry_0_views.xml',
        'views/offboard_desk_item_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
