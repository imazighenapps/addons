# -*- coding: utf-8 -*-
{
    'name': 'MarginBook',
    'version': '19.0.1.0.0',
    'summary': 'Show the realized margin of every confirmed order and invoice, line by line, without leaving the sale.',
    'description': '''MarginBook - Margins Without Guesswork
======================================
The order was confirmed because the deal was "good". Three months
later, nobody can say how good it really was: the revenue sits in the
sale, the cost sits in three different places, and the margin
conversation turns into an opinion contest at the monthly meeting.

MarginBook records the realized margin of every confirmed order, line
by line, without leaving the sale. One margin sheet names the order,
the customer, the salesperson and the date, and each of its lines
carries the quantity, the selling price and the unit cost actually
incurred. Revenue, cost, net margin and margin rate are computed from
the lines, never retyped, and the sheet is flagged the moment its rate
slips under the target margin. Confirming the sheet freezes its lines
so the realized story cannot be rewritten after the fact, and the
low-margin screen points at the lines that eat the profit before the
next negotiation opens.

* One margin sheet per order with customer, salesperson and date.
* Lines with quantity, selling price and unit cost incurred.
* Revenue, cost, net margin and margin rate computed live.
* A target margin per sheet and an under-target flag.
* Confirming freezes the lines: the margin cannot be edited back.
* The detail screen breaks the margin down line by line.
* The low-margin screen lists the lines that lose money.
* Multi-company isolation out of the box.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Sales/Sales',
    'license': 'OPL-1',
    'price': 49.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'views/margin_book_0_views.xml',
        'views/margin_book_line_1_views.xml',
        'views/margin_book_worst_2_views.xml',
        'views/menus.xml',
        'views/margin_book_worst_action.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
