# -*- coding: utf-8 -*-
{
    'name': 'PriceShift',
    'version': '19.0.1.0.0',
    'summary': 'Decide the next price increase once, schedule its effective date and see exactly when each customer moved.',
    'description': '''PriceShift - One Date, Every Price
==================================
The catalogue goes up 4% on 1 January, and three weeks later
salespeople still quote the old price, the system carries no record of
who was told and when, and the finance director cannot say which
customers actually moved. Price lists are updated by hand, one product
at a time, and the trace of the decision dies with the spreadsheet.

PriceShift decides the change once. One record carries the type of the
move - increase or decrease - the percentage and the effective date,
and one line per customer names who is moving, the price paid today and
the price to pay after the date. The new price is computed, not
retyped, so nobody invents a rounding. Scheduling locks the rule and
the percentage, applying stamps the exact date and freezes every line,
and cancelling keeps the story instead of deleting anything. The
applied screen answers the audit question line by line: when did this
customer change, and from how much to how much.

* One change record for the increase or the decrease, in percent.
* One line per customer with its current and computed new price.
* One effective date decided once and visible on the record.
* Scheduling locks the rule and the percentage.
* Applying stamps the date and freezes every line, no silent retyping.
* Cancelling keeps the full trace instead of deleting the decision.
* The applied screen lists exactly when each customer moved.
* Multi-company isolation out of the box.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Sales/Sales',
    'license': 'OPL-1',
    'price': 59.0,
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
        'views/price_shift_0_views.xml',
        'views/price_shift_line_1_views.xml',
        'views/price_shift_applied_2_views.xml',
        'views/menus.xml',
        'views/price_shift_applied_action.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
