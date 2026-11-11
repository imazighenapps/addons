# -*- coding: utf-8 -*-
{
    'name': 'CountDesk',
    'version': '20.0.1.0.0',
    'summary': 'Print and run blind stock count sheets per location and sign off the result with the counter identified.',
    'description': '''CountDesk - Counts You Can Trust
================================
Print and run blind stock count sheets per location and sign off the result with the counter identified.

Key points:
* Count sheets tracked in a dedicated register.
* Blind counts recorded with clear ownership and dates.
* Count sign-off visible so nothing slips through.
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
    'price': 39.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.access.csv',
        'views/stock_count_entry_0_views.xml',
        'views/stock_count_item_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
