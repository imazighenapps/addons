# -*- coding: utf-8 -*-
{
    'name': 'ChannelRate',
    'version': '18.0.1.0.0',
    'summary': 'Maintain a distinct price list and margin target per sales channel and compare performance channel by channel.',
    'description': '''ChannelRate - Every Channel, Its Margin
=======================================
Maintain a distinct price list and margin target per sales channel and compare performance channel by channel.

Key points:
* Sales channels tracked in a dedicated register.
* Channel rates recorded with clear ownership and dates.
* Channel margin visible so nothing slips through.
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
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'views/channel_price_entry_0_views.xml',
        'views/channel_price_item_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
