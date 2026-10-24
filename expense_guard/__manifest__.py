# -*- coding: utf-8 -*-
{
    'name': 'ExpenseGuard - Expense Policy Compliance',
    'version': '19.0.1.0.0',
    'summary': 'Control expense claims against your own policy: amount caps, receipt required, maximum age, duplicate check, block or warn, with an audit trail.',
    'description': '''ExpenseGuard - Expense Policy Compliance
========================================
No more blind approval of out-of-policy expense claims.

ExpenseGuard adds a real policy engine on top of Odoo expenses. For each
category you define a maximum amount, whether a receipt is mandatory and how
old an expense may be. When the employee submits, ExpenseGuard blocks the
claim or warns the approver, and records every violation in an audit trail.

* Policies per expense category, per company.
* Maximum amount, receipt required, maximum age.
* Block mode or warning mode.
* Violations recorded in a permanent audit trail.
* Clear message on the expense and in the chatter.
* Report of violations by policy and by employee.
* Works with the standard Odoo expense module.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'category': 'Human Resources/Expenses',
    'license': 'OPL-1',
    'price': 49.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
        'hr_expense',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/expense_policy_0_views.xml',
        'views/expense_audit_1_views.xml',
        'views/menus.xml',
        'views/expense_inherit.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
