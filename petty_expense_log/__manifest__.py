# -*- coding: utf-8 -*-
{
    'name': 'PettyExpenseLog',
    'version': '18.0.1.0.0',
    'summary': 'Record petty expense requests with amount, purpose, approval and reimbursement states for simple tracking.',
    'description': '''PettyExpenseLog - Petty Expense Request Register
================================================
Small expenses submitted informally are hard to approve, reimburse and audit.

PettyExpenseLog provides a simple request and reimbursement register.

* Expense requests with requester, date and amount.
* Category/purpose and notes.
* Approver and reimbursement tracking.
* Draft, submitted, approved, reimbursed and rejected states.
* Request history.
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
        'hr',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'data/sequence.xml',
        'views/petty_expense_log_0_views.xml',
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
