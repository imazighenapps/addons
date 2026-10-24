# -*- coding: utf-8 -*-
{
    'name': 'StatementPro - Customer and Supplier Statements',
    'version': '18.0.1.0.0',
    'summary': 'Consolidated account statements per partner: opening balance, movements, aging, PDF and batch sending.',
    'description': '''StatementPro - Customer and Supplier Statements
===============================================
Give every customer and supplier a clean, professional statement in one click.

StatementPro rebuilds the account statement from posted journal items: the
opening balance, every movement of the period, the closing balance and the
aging by due date. The PDF is ready to send, and the batch wizard produces
one statement per partner for the whole month.

* One statement per partner, customer or supplier.
* Opening balance, debits, credits and closing balance, always reconciled.
* Aging by due date, with overdue amount and days late.
* Professional PDF with your company layout.
* Batch wizard: generate statements for 100 partners in one action.
* Multi-company and multi-currency.
* Full audit trail on generation and sending.''',
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
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/statement_run_0_views.xml',
        'views/statement_batch_1_views.xml',
        'views/menus.xml',
        'report/statement_report.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
