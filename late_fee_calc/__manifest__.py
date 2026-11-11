# -*- coding: utf-8 -*-
{
    'name': 'LateFee',
    'version': '20.0.1.0.0',
    'summary': 'Compute the statutory late payment interest on overdue invoices at the legal rate and issue the debit lines.',
    'description': '''LateFee - Late Costs What It Should
===================================
When a customer pays late, the statutory interest is owed but rarely
claimed: the rate lives in a note, the number of days is counted by
hand, and the debit line is issued weeks after it should have been.
Money left on the table is still money.

LateFee computes late payment interest in Odoo from simple, auditable
inputs. Define an interest rule with the legal annual rate and an
optional fixed fee, register each overdue invoice with its partner, due
date, amount and the payment or calculation date, and let the module
compute the days late and the interest due. Each interest line can be
moved from draft to issued when you are ready to claim it, and the
total claimed stays visible on the rule. The calculation is dated,
repeatable and ready to back the debit you send.

* Interest rules with an annual statutory rate and optional fixed fee.
* Overdue invoice lines with partner, due date and amount due.
* Days late and interest amount computed and stored for you.
* Draft and issued states with a clear claim workflow.
* Totals per rule to see how much interest has been issued.
* Guards that refuse negative amounts or impossible dates.
* Manual recalculation action to refresh the computed interest.
* Multi-company isolation out of the box.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Accounting/Accounting',
    'license': 'OPL-1',
    'price': 49.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.access.csv',
        'views/late_fee_rule_0_views.xml',
        'views/late_fee_line_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
