# -*- coding: utf-8 -*-
{
    'name': 'OnTime',
    'version': '19.0.1.0.0',
    'summary': 'Compare the delivery date promised on each order with what the warehouse really shipped and score your on-time rate.',
    'description': '''OnTime - Promised, Then Delivered
=================================
Every order confirmation carries a delivery date, and every customer
remembers the one that slipped. When the exact question comes - were
we on time in October - the honest answer is a feeling: sales say the
warehouse is slow, the warehouse says sales overpromise, and nobody
supports either side with a number.

OnTime watches one commitment per order: the date you promised, the
date the goods really shipped and the delay between them, computed and
stored the day the shipment is recorded. Ships early or on the day and
the commitment counts as on time; ships after the promise and the
delay shows in days, in black and white. The late screen gathers the
orders that missed their promise, and the on-time screen keeps the
score side by side with each promise. The promise you gave the customer
stops being decoration, it becomes the metric the whole company reads.

* One delivery commitment per order, with its promise date.
* The real shipment date recorded in one click.
* The delay in days, computed and stored on each shipment.
* Early and on-time deliveries both scored as on time.
* One late screen of the orders that missed the promise.
* One on-time screen to score the promise book as a whole.
* A shipment without its date is refused for you.
* Multi-company isolation out of the box.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Sales/Sales',
    'license': 'OPL-1',
    'price': 45.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'views/otd_commitment_0_views.xml',
        'views/otd_score_1_views.xml',
        'views/otd_late_2_views.xml',
        'views/menus.xml',
        'views/otd_score_action.xml',
        'views/otd_late_action.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
