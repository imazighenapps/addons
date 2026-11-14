# -*- coding: utf-8 -*-
{
    'name': 'SalePlan Pay',
    'version': '20.0.1.0.0',
    'summary': 'Split a confirmed sale order into dated installments matching the order total, generate a draft invoice per installment in one click, and track planned, invoiced, paid and late installments in a company-safe view.',
    'description': '''SalePlan Pay - Installment Plans on Sales
=========================================
B2B sellers who grant payments in several installments recreate every due
date as a hand-written draft invoice and chase late payers from memory.
Odoo Community offers a single down payment and payment terms on the whole
invoice, but no scheduled plan with a status per installment.

SalePlan Pay adds a payment plan to a confirmed sale order. Define N
installments with an amount and a due date: the plan is refused if the
sum does not match the order amount. From each installment, generate a
draft invoice in one click, pre-filled with the installment amount and
label. Each installment shows a computed status - planned, invoiced, paid
or late - so the team sees what is expected, billed and overdue. A simple
late view groups overdue installments by customer.

* Payment plan on a confirmed sale order with N dated installments.
* Control: the sum of installments must equal the order amount.
* One-click draft invoice generation per installment (no duplicate).
* Computed status: planned, invoiced, paid, late.
* Kanban and report view of late installments by customer.
* Multi-company, no Enterprise dependency, no external Python package.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Sales/Sales',
    'license': 'OPL-1',
    'price': 69.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'sale',
        'account',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.access.csv',
        'data/sequence.xml',
        'views/sale_plan_pay_0_views.xml',
        'views/sale_plan_pay_line_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
