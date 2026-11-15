# -*- coding: utf-8 -*-
{
    'name': 'EmployeeAdvance',
    'version': '18.0.1.0.0',
    'summary': 'Track employee cash advances from request to clearing, record partial expense or cash returns, and keep the outstanding balance per advance and per employee in a company-safe register.',
    'description': '''EmployeeAdvance - Cash Advances and Clearing
============================================
Cash advances given to employees for travel or purchases are easy to hand out
and hard to close: spreadsheets drift, receipts arrive late and nobody knows
how much each person still owes the company.

EmployeeAdvance provides a dedicated register for employee advances. Record the
requested and approved amount, move the advance through a clear workflow and
log every clearing as an expense justification or a cash return. The outstanding
balance is computed automatically so managers can see what is paid, what is
partially cleared and what remains due.

* Advance requests per employee with purpose, date and amounts.
* Workflow: draft, approved, paid, partially cleared, cleared, cancelled.
* Clearing lines (expense justification or cash return) reduce the balance.
* Outstanding balance computed per advance; cannot be cleared beyond paid.
* Search and group by employee, state and period.
* Multi-company, no Enterprise dependency, no external Python package.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Human Resources/Employee',
    'license': 'OPL-1',
    'price': 49.0,
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
        'views/employee_advance_0_views.xml',
        'views/employee_advance_clearing_1_views.xml',
        'views/menus.xml',
    ],
    'demo': [
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
