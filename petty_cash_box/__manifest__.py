# -*- coding: utf-8 -*-
{
    'name': 'PettyCash Box',
    'version': '19.0.1.0.0',
    'summary': 'Manage petty cash boxes with opening balance, categorized in and out movements, running balance and periodic cash counts to reconcile expected versus counted cash per company.',
    'description': '''PettyCash Box - Petty Cash Fund Movements and Balance
=====================================================
Petty cash funds are convenient but opaque: receipts pile up in a box, the
running balance is unknown and month-end reconciliation becomes guesswork.

PettyCash Box gives each fund a clear register. Define a box with its responsible
user, currency and opening balance, record every top-up and expense as a dated
movement, and see the expected balance at any time. Periodic cash counts record
what was actually in the box and highlight the difference so discrepancies can be
investigated.

* Petty cash boxes per company with responsible user and currency.
* Movements: top-up, expense and adjustment with date and category.
* Running expected balance computed from opening balance and movements.
* Cash counts comparing expected and counted amounts with difference.
* Search and group by box, type, category and period.
* Multi-company, no Enterprise dependency, no external Python package.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Accounting/Accounting',
    'license': 'OPL-1',
    'price': 39.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'data/sequence.xml',
        'views/petty_cash_box_0_views.xml',
        'views/petty_cash_movement_1_views.xml',
        'views/petty_cash_count_2_views.xml',
        'views/petty_cash_category_3_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
