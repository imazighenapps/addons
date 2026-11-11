# -*- coding: utf-8 -*-
{
    'name': 'WinLoss',
    'version': '19.0.1.0.0',
    'summary': 'Capture why each opportunity was won or lost and turn the reasons into a report your sales lead can act on.',
    'description': '''WinLoss - Learn From Every Deal
===============================
Capture why each opportunity was won or lost and turn the reasons into a report your sales lead can act on.

Key points:
* Lost deals tracked in a dedicated register.
* Loss reasons recorded with clear ownership and dates.
* Won patterns visible so nothing slips through.
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
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'views/win_loss_entry_0_views.xml',
        'views/win_loss_item_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
