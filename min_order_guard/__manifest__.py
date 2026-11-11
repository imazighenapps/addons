# -*- coding: utf-8 -*-
{
    'name': 'OrderMin',
    'version': '20.0.1.0.0',
    'summary': 'Enforce minimum order value or quantity per customer with a clean exception log for the orders you allow anyway.',
    'description': '''OrderMin - Minimums, Enforced Politely
======================================
You promised thresholds to your logistics: two hundred euros per
delivery or fifty pieces, because below that the picking, the packing
and the transport cost more than the margin. Then a beloved customer
orders ninety euros of goods, the rep does not want to say no, and the
minimum becomes a rumor. The warehouse still proceses the small parcel,
still pays the carrier, and nobody knows which exceptions were allowed
by whom.

OrderMin holds one rule per customer with a minimum amount, a minimum
quantity or both, and turns every order below the threshold into an
exception with its reference, its value, its shortfall and its state.
No exception moves without an explicit decision: allowing one requires
a written reason and stamps the date and the person who accepted the
risk, refusing one is a single click with the same trail. The log
screen keeps the whole history clean: by customer, by rule, decided or
still waiting. The minimum stops being folklore and becomes a ledger.

* One rule per customer with amount, quantity or both.
* The shortfall computed and stored on every exception.
* An explicit decision for every order below the minimum.
* A written reason required when you allow an exception.
* The date and the decision maker stamped on each refusal.
* One exception log of everything that came in under threshold.
* A rule without any minimum is refused for you.
* Multi-company isolation out of the box.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Sales/Sales',
    'license': 'OPL-1',
    'price': 39.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.access.csv',
        'views/order_min_rule_0_views.xml',
        'views/order_min_exception_1_views.xml',
        'views/order_exceptions_2_views.xml',
        'views/menus.xml',
        'views/order_exceptions_action.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
