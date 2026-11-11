# -*- coding: utf-8 -*-
{
    'name': 'QuotePing',
    'version': '20.0.1.0.0',
    'summary': 'Watch quotations age day by day and remind your salespeople before a deal quietly dies in the pipeline.',
    'description': '''QuotePing - Deals Never Die Quietly
===================================
A quotation sent without a follow-up date is a promise with no owner.
Two weeks later the customer bought elsewhere, the salesperson says the
deal was still warm, and nobody can say which quotes are actually
sleeping in the pipeline right now.

QuotePing watches every quotation day by day. One tracker names the
quote, the customer, the salesperson and the amount, and carries the
reminder plan: how often to follow up and how many attempts the deal
deserves. Every reminder is stamped with its date, its channel - email,
phone or meeting - and the outcome, and the due flag lights up as soon
as the next reminder is late. The log counts itself, and the maximum
number of attempts is enforced so a deal is never pestered past the
point of politeness. Winning or losing the deal closes the tracker, and
the closed screen keeps the reminder history as the evidence that the
pipeline was worked, not watched.

* One tracker per quotation with customer, salesperson and amount.
* A reminder plan: interval in days and maximum attempts per deal.
* Reminders stamped with date, channel - email, phone or meeting.
* A due flag computed from the plan, not from opinion.
* One click to remind: the log counts itself.
* The maximum number of attempts is enforced for you.
* Won and lost close the tracker and keep the evidence.
* Multi-company isolation out of the box.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Sales/Sales',
    'license': 'OPL-1',
    'price': 29.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.access.csv',
        'data/sequence.xml',
        'views/quote_watch_0_views.xml',
        'views/quote_nudge_1_views.xml',
        'views/quote_watch_closed_2_views.xml',
        'views/menus.xml',
        'views/quote_watch_closed_action.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
