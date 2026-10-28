# -*- coding: utf-8 -*-
{
    'name': 'PettyCashPro - Petty Cash Fund Management',
    'version': '20.0.1.0.0',
    'summary': 'Manage petty cash funds, top-ups, expenses with receipts, reconciliations and closures, with a live balance and an explained gap.',
    'description': '''PettyCashPro - Petty Cash Fund Management
========================================
A petty cash box without a ledger is a leak.

PettyCashPro gives every cash box its own fund, with an initial float, a
responsible person and a live balance. Each top-up, expense and return is a
transaction, and every expense can carry its receipt. At any time you
reconcile the counted cash against the theoretical balance; a gap must be
explained before the fund can be closed.

* One fund per cash box, with a unique code and a responsible.
* Initial float, top-ups, expenses and returns.
* Live balance and totals per fund.
* Receipt attached to every transaction.
* Confirmation workflow with the user and the timestamp.
* Reconciliation with counted cash and difference.
* Closing blocked until the gap is explained.
* Multi-company and multi-currency.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'category': 'Accounting/Accounting',
    'license': 'OPL-1',
    'price': 49.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
        'account',
    ],
    'data': [
        'security/security.xml',
        'security/ir.access.csv',
        'views/petty_cash_fund_0_views.xml',
        'views/petty_cash_transaction_1_views.xml',
        'views/petty_cash_reconciliation_2_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
