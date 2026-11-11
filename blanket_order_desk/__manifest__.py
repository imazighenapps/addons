# -*- coding: utf-8 -*-
{
    'name': 'BlanketDesk',
    'version': '20.0.1.0.0',
    'summary': 'Manage framework orders with scheduled call-offs and always know the quantity and value still to release.',
    'description': '''BlanketDesk - Call Off With Confidence
======================================
Manage framework orders with scheduled call-offs and always know the quantity and value still to release.

Key points:
* Blanket orders tracked in a dedicated register.
* Call-offs recorded with clear ownership and dates.
* Remaining qty visible so nothing slips through.
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
    'price': 69.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.access.csv',
        'views/blanket_order_entry_0_views.xml',
        'views/blanket_order_item_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
