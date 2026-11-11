# -*- coding: utf-8 -*-
{
    'name': 'TravelDesk',
    'version': '20.0.1.0.0',
    'summary': 'Request, approve and track business trips with the expected costs and the receipts collected on return.',
    'description': '''TravelDesk - Trips Planned And Traced
=====================================
Request, approve and track business trips with the expected costs and the receipts collected on return.

Key points:
* Travel requests tracked in a dedicated register.
* Trip approvals recorded with clear ownership and dates.
* Travel costs visible so nothing slips through.
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
        'views/travel_desk_entry_0_views.xml',
        'views/travel_desk_item_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
