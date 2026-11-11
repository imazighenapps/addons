# -*- coding: utf-8 -*-
{
    'name': 'AccrualBook',
    'version': '20.0.1.0.0',
    'summary': 'Record the month-end accruals for services received but not billed and reverse them automatically next month.',
    'description': '''AccrualBook - Book It, Reverse It
=================================
At month end the invoices are not all in, yet the expense belongs to the
period. Teams keep accruals in a spreadsheet, forget to reverse them
the following month, and the same charge quietly lands twice when the
supplier bill finally arrives.

AccrualBook keeps a dated register of every month-end accrual in Odoo.
Record the service, the partner, the period, the amount and the planned
reversal date, then book the accrual when the period closes. When the
next month opens, reverse it with one action: the reversal date is
stamped and the entry moves out of the open queue. Owners can see their
own accruals, and the history of what was booked and reversed stays in
the chatter. Nothing is lost in a spreadsheet and nothing is booked
twice.

* A dated register of month-end accruals per period.
* Partner, amount, owner and planned reversal date on every entry.
* Draft, booked and reversed states with a clear workflow.
* One-click reversal that stamps the effective reversal date.
* Open accruals queue for what still needs to be reversed.
* Validation that refuses a reversal before the accrual is booked.
* Amounts and dates guarded against impossible values.
* Multi-company isolation out of the box.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Accounting/Accounting',
    'license': 'OPL-1',
    'price': 69.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.access.csv',
        'views/accrual_entry_0_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
