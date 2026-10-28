# -*- coding: utf-8 -*-
{
    'name': 'DepositPro - Customer Deposits and Prepayments',
    'version': '20.0.1.0.0',
    'summary': 'Register customer deposits and prepayments, apply them to posted invoices, track the remaining balance, refund it and report on it.',
    'description': '''DepositPro - Customer Deposits and Prepayments
==============================================
Money received before the invoice is not revenue yet. It is a liability, and
it has to be followed, applied and refunded without losing the thread.

DepositPro keeps a numbered register of every customer deposit, with its
payment method, journal and reference. When the invoice is posted you apply
the deposit against it, partially or fully. The remaining balance is always
visible, the status changes by itself, and a refund closes the loop with a
date and a reason.

* Numbered deposit register (DEP/YYYY/0001).
* Bank, cash, card or cheque payment method, with an optional journal.
* Allocation against posted customer invoices and credit notes.
* Partial and full application, with automatic status update.
* Remaining balance recomputed on every allocation, edit or deletion.
* Refund of the remaining balance, with date and reason.
* Customer and status filters, totals per customer.
* Multi-company and multi-currency.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'category': 'Accounting/Accounting',
    'license': 'OPL-1',
    'price': 69.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
        'account',
    ],
    'data': [
        'security/security.xml',
        'security/ir.access.csv',
        'data/sequence.xml',
        'views/customer_deposit_0_views.xml',
        'views/deposit_allocation_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
