# -*- coding: utf-8 -*-
{
    'name': 'DealDesk',
    'version': '20.0.1.0.0',
    'summary': 'Register every non-standard commercial deal, route it for approval and keep the exceptions out of side emails.',
    'description': '''DealDesk - Exceptions On The Record
===================================
Register every non-standard commercial deal, route it for approval and keep the exceptions out of side emails.

Key points:
* Special deals tracked in a dedicated register.
* Deal approvals recorded with clear ownership and dates.
* Deal register visible so nothing slips through.
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
    'price': 59.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.access.csv',
        'views/deal_desk_entry_0_views.xml',
        'views/deal_desk_item_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
