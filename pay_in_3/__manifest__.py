# -*- coding: utf-8 -*-
{
    'name': 'PayIn3',
    'version': '19.0.1.0.0',
    'summary': 'Split a customer invoice into two, three or four dated installments, track what is paid, and register the payment of each installment without leaving the invoice.',
    'description': '''PayIn3 - Invoice Payment Plans
==============================
A customer asks to pay in three times. The invoice is sent as a single
amount, the first transfer arrives, and then the invoice stays open at its
full balance while somebody keeps a mental note of what is left. At the
second reminder, nobody remembers whether the second installment was the
one that arrived in June.

PayIn3 splits the invoice into a dated plan. Each installment carries its
date and its amount, the sum matches the invoice total to the cent, and the
last installment absorbs the rounding difference. Confirming the plan
freezes the schedule; marking an installment paid updates the plan balance,
and the payment button opens the standard Odoo payment wizard with the
right amount and date already filled in. The invoice keeps its own amount:
the plan is a schedule, not an accounting entry.

* Plans of two, three or four installments, or any count.
* Dates computed from a first due date and an interval.
* Sum equal to the invoice total, rounding on the last installment.
* Paid amount, remaining amount and progress on the plan.
* One click to open the payment wizard with the right amount.
* Draft, active, done and cancelled states.
* Recompute while nothing is paid, with a guard once it is.
* Kanban, graph and pivot, multi-company isolation.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Accounting/Accounting',
    'license': 'OPL-1',
    'price': 69.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'account',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'views/payment_plan_0_views.xml',
        'views/payment_plan_line_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
