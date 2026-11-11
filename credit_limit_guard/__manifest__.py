# -*- coding: utf-8 -*-
{
    'name': 'CreditGuard',
    'version': '19.0.1.0.0',
    'summary': 'Set a credit limit per customer, watch open exposure in real time and block confirmation when the line is crossed.',
    'description': '''CreditGuard - Exposure Under Control
====================================
Set a credit limit per customer, watch open exposure in real time and block confirmation when the line is crossed.

Key points:
* Credit limits tracked in a dedicated register.
* Exposure recorded with clear ownership and dates.
* Blocked orders visible so nothing slips through.
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
        'views/credit_limit_entry_0_views.xml',
        'views/credit_limit_item_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
