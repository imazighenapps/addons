# -*- coding: utf-8 -*-
{
    'name': 'FeedbackLog',
    'version': '20.0.1.0.0',
    'summary': 'Log customer feedback with satisfaction score, topic and follow-up state, link it to customers and orders, and report trends by score, topic and period in a company-safe register.',
    'description': '''FeedbackLog - Customer Feedback and Satisfaction Tracking
========================================================
Customer feedback arrives by email, phone and meetings but rarely becomes a
structured record. Without a consolidated log, recurring issues stay hidden and
unhappy customers are followed up too late.

FeedbackLog captures each feedback entry with the customer, channel, satisfaction
score, topic and comment. A simple follow-up workflow tracks whether the feedback
is new, in progress or resolved, and reports reveal trends by score, topic and
period.

* Feedback entries per customer with date, channel and contact.
* Satisfaction score and configurable topics/categories.
* Follow-up workflow: new, in progress, done with responsible user.
* Optional link to a sale order reference for context.
* Search and reporting by score, topic, state and period.
* Multi-company, no Enterprise dependency, no external Python package.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Sales/Sales',
    'license': 'OPL-1',
    'price': 49.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'sale',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.access.csv',
        'data/sequence.xml',
        'views/customer_feedback_0_views.xml',
        'views/customer_feedback_topic_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
