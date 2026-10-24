# -*- coding: utf-8 -*-
{
    'name': 'DupliPay - Duplicate Invoice and Payment Detection',
    'version': '19.0.1.0.0',
    'summary': 'Detect duplicate invoices, bills and payments before payment, with a tolerance on amount and date and a documented decision.',
    'description': '''DupliPay - Duplicate Invoice and Payment Detection
==================================================
Paying the same bill twice is easy. Getting the money back is hard.

DupliPay scans your posted invoices, vendor bills and payments, compares
partner, amount, date and reference, and raises an alert when two records
look like the same transaction. You decide: real duplicate, or legitimate.
Every decision is traced.

* Scan invoices, vendor bills and payments.
* Tolerance on amount and number of days, configurable.
* Reference similarity to reduce false positives.
* One alert per pair, never duplicated.
* Decision workflow: ignore or mark as duplicate.
* Full audit trail with the user and the date.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'category': 'Accounting/Accounting',
    'license': 'OPL-1',
    'price': 59.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
        'account',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/dupli_alert_0_views.xml',
        'views/dupli_rule_1_views.xml',
        'views/menus.xml',
        'data/cron.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
