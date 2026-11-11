# -*- coding: utf-8 -*-
{
    'name': 'PromiseDesk',
    'version': '20.0.1.0.0',
    'summary': 'Track promised delivery dates on backordered lines and send consistent updates when supply dates move.',
    'description': '''PromiseDesk - Promises Kept, Dates Clear
========================================
Track promised delivery dates on backordered lines and send consistent updates when supply dates move.

Key points:
* Promised dates tracked in a dedicated register.
* Backorder lines recorded with clear ownership and dates.
* Customer updates visible so nothing slips through.
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
        'views/backorder_promise_entry_0_views.xml',
        'views/backorder_promise_item_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
