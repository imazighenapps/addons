# -*- coding: utf-8 -*-
{
    'name': 'PayAdvance',
    'version': '18.0.1.0.0',
    'summary': 'Handle salary advances with an approved request, a repayment schedule and the balance always visible.',
    'description': '''PayAdvance - Advances With A Plan
=================================
Salary advances move fast when an employee needs cash, but the agreement
often lives in an email thread while the repayment happens line by line
on the payslip. Finance loses sight of what was approved, what was paid
back and what is still due, and the employee hears a different balance
every month.

PayAdvance turns each salary advance into an approved request with a
clear amount, date and purpose, then spreads the repayment across a
dated schedule that payroll can follow. Every repayment line tracks its
amount and paid status so the remaining balance is always computed and
stored, not guessed. A refusal or a fully repaid advance closes the file
with a clear state, and the request stays blocked if its schedule would
exceed the approved amount. Multi-company isolation keeps each company
in its own book.

* A salary advance request per employee with amount and approval date.
* A repayment schedule with dated installments per request.
* Paid installments and a stored remaining balance on every request.
* A workflow to submit, approve, refuse and close repaid advances.
* The request refuses a repayment plan above the approved amount.
* One screen to see balances and repayment progress at a glance.
* Employee-linked requests for HR payroll follow-up.
* Multi-company isolation out of the box.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Human Resources/Employee',
    'license': 'OPL-1',
    'price': 49.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
        'hr',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'views/advance_request_0_views.xml',
        'views/advance_repayment_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
