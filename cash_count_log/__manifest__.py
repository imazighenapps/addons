# -*- coding: utf-8 -*-
{
    'name': 'CashCountLog',
    'version': '19.0.1.0.0',
    'summary': 'Record cash counts with expected and counted amounts, computed difference, notes and validation states for reconciliation.',
    'description': '''CashCountLog - Cash Count and Reconciliation Register
=====================================================
Cash counts recorded on paper make discrepancies hard to track and audit.

CashCountLog provides a simple register for each count with reconciliation.

* Count records with date, location/register and counter.
* Expected amount, counted amount and computed difference.
* Discrepancy notes and reviewer.
* Draft, submitted and validated states.
* Count history and variance tracking.
* Multi-company, no Enterprise dependency, no external Python package.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Accounting/Accounting',
    'license': 'OPL-1',
    'price': 29.0,
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
        'views/cash_count_log_0_views.xml',
        'views/menus.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
