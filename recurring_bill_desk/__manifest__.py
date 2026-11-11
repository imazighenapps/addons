# -*- coding: utf-8 -*-
{
    'name': 'RecurringBill',
    'version': '19.0.1.0.0',
    'summary': 'Generate recurring vendor bills on a schedule for rent, subscriptions and services you pay every period.',
    'description': '''RecurringBill - Bills That Arrive On Time
=========================================
Generate recurring vendor bills on a schedule for rent, subscriptions and services you pay every period.

Key points:
* Recurring vendors tracked in a dedicated register.
* Bill schedule recorded with clear ownership and dates.
* Generated bills visible so nothing slips through.
* Draft, confirmed and done states with an audit trail.
* Computed totals and counts kept up to date.
* Active flag to archive records no longer needed.
* Company-aware records for multi-company use.
* Mail chatter for notes and follow-up.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Accounting/Accounting',
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
        'views/recurring_bill_entry_0_views.xml',
        'views/recurring_bill_item_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
