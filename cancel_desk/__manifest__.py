# -*- coding: utf-8 -*-
{
    'name': 'CancelDesk',
    'version': '18.0.1.0.0',
    'summary': 'Log every cancelled order with a reason, the lost value and who decided, and turn the pattern into decisions.',
    'description': '''CancelDesk - Every Cancel Explained
===================================
The order was cancelled, the line disappears from the pipeline, and
with it the reason, the amount and the name of the person who decided.
Next quarter the same customer cancels the same way for the same
reason, and the meeting only notices the revenue - the pattern never
surfaces.

CancelDesk keeps every cancellation. One record names the cancelled
order, the customer, the salesperson and the responsible, the loss
date, the lost value and the reason: a price beaten elsewhere, a
delivery delay, a product mismatch, a competitor or anything you
classify yourself. Writing off the loss closes the file with a dated
stamp, or a replacement order turns the cancellation into recovered
value, registered with its reference and its amount, and the sheet
flips itself to recovered once the lost value is fully won back. The
reason counters say why revenue actually disappears, and the recovered
screen is the one the manager reads before discounting anything again.

* One cancellation record with order, customer and responsible.
* The exact lost value of the order and the decision date.
* A reason per cancellation: price, delivery, product, competitor.
* Write off the loss with a dated stamp.
* Recoveries with the new order, the amount and the date.
* The sheet flips to recovered once the value is fully won back.
* Reason counters show why revenue actually disappears.
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
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'data/sequence.xml',
        'views/cancel_log_0_views.xml',
        'views/cancel_recovery_1_views.xml',
        'views/cancel_recovered_2_views.xml',
        'views/menus.xml',
        'views/cancel_recovered_action.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
