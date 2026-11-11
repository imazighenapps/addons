# -*- coding: utf-8 -*-
{
    'name': 'ReorderPlan',
    'version': '18.0.1.0.0',
    'summary': 'See how many days of demand your stock covers per product and turn every skimpy line into a planned purchase.',
    'description': '''ReorderPlan - Days Of Stock, Planned
====================================
Stock answers the question "how much is on hand" but buyers need to know
"for how many days". A healthy quantity can hide a fast-moving product that
runs out next week, while a small pile can last months on a slow line. The
decision to reorder is made in a spreadsheet, too late, after the shelf is
already empty.

ReorderPlan keeps one coverage line per product: the quantity on hand, the
daily demand and the minimum days you want to hold. The covered days are
computed and stored on every line, so a skimpy product is visible at once.
When coverage drops below the minimum, the line is flagged and the buyer can
turn it into a planned purchase with a planned quantity. A below-minimum
screen shows every exposed product instead of a guessing game. The plan the
buyer needs is the one the module already produces.

* A coverage line per product with on-hand quantity and company.
* Daily demand and minimum days defined on every line.
* Covered days computed and stored for reliable filtering.
* Skimpy lines flagged automatically below the minimum.
* A planned purchase quantity recorded per exposed product.
* Decision states from draft to planned and ordered.
* Daily demand and minimum days must stay positive.
* Multi-company isolation out of the box.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Purchase/Purchase',
    'license': 'OPL-1',
    'price': 69.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'views/coverage_item_0_views.xml',
        'views/coverage_item_low_1_views.xml',
        'views/menus.xml',
        'views/coverage_item_low_action.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
