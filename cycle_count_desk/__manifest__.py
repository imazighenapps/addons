# -*- coding: utf-8 -*-
{
    'name': 'CycleCount',
    'version': '20.0.1.0.0',
    'summary': 'Plan rolling cycle counts by location and ABC class and record every variance with a reason and owner.',
    'description': '''CycleCount - Accuracy Without Shutdowns
=======================================
Plan rolling cycle counts by location and ABC class and record every variance with a reason and owner.

Key points:
* Count plan tracked in a dedicated register.
* Count tasks recorded with clear ownership and dates.
* Variance log visible so nothing slips through.
* Draft, confirmed and done states with an audit trail.
* Computed totals and counts kept up to date.
* Active flag to archive records no longer needed.
* Company-aware records for multi-company use.
* Mail chatter for notes and follow-up.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Inventory/Inventory',
    'license': 'OPL-1',
    'price': 69.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.access.csv',
        'views/cycle_count_entry_0_views.xml',
        'views/cycle_count_item_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
