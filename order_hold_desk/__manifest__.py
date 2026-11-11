# -*- coding: utf-8 -*-
{
    'name': 'HoldDesk',
    'version': '18.0.1.0.0',
    'summary': 'Place a confirmed order on hold for credit, stock, quality or commercial reasons, and release it with a dated trace.',
    'description': '''HoldDesk - A Hold With A Reason
===============================
A confirmed order enters the warehouse, then credit control calls: the
customer is over its limit and the shipment has to be stopped by hand.
The stop lives in a chat message, the release happens two days later
with no trace of who decided, and the teams argue about which orders
are actually blocked. Nobody can answer the simple question: how many
confirmed orders are on hold right now, and why?

HoldDesk gives every suspension one Odoo record. A hold names the order
it freezes, the customer, the amount at stake, the reason - credit,
stock, quality, commercial or another rule you define - and the date it
was placed. Releasing the order stamps the exact date, the user who
unblocked it and the number of days the money waited, and every
decision lands in the chatter. The active-holds screen is the daily
review list: nothing hides in a comment, and the audit trail the
manager asks for already exists.

* One hold record per blocked order, with its amount and customer.
* A reason per hold: credit, stock, quality, commercial or custom.
* Placing an order on hold takes one click and keeps its order date.
* Release stamps the date, the user and the days the money waited.
* The active-holds screen lists everything still frozen.
* A hold cannot be released twice or before it is even on hold.
* Reason counters show which rule blocks your revenue most often.
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
        'views/hold_reason_0_views.xml',
        'views/hold_request_1_views.xml',
        'views/hold_active_2_views.xml',
        'views/menus.xml',
        'views/hold_active_action.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
