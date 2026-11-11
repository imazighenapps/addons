# -*- coding: utf-8 -*-
{
    'name': 'SampleKit',
    'version': '18.0.1.0.0',
    'summary': 'Track the samples you hand to prospects: to whom, when, consumed or returned, with the follow-up they deserve.',
    'description': '''SampleKit - Samples That Sell Or Come Back
==========================================
Samples vanish. A swatch leaves with a prospect, a demo unit goes out
for two weeks, and the follow-up nobody planned lets it turn into
furniture in the client's office. When the same prospect finally calls
to order, the sample you lent is everywhere except where the team can
see it. The budget for samples doubles, the return rate stays a mystery
and the order that justified the sample never gets linked to it.

SampleKit keeps a catalog of every sample you hand out, with its
category and its follow-up delay. Each hand-out names the recipient,
the quantity and the date, and computes the date the follow-up is due
from the delay of the sample. The state says exactly where the unit
stands: with the prospect, consumed by the test or returned. A
one-click action marks the order it turned into, so the cost of the
sample is finally attached to a sale. The follow-up queue lists every
sample still outside without a pending order, in the order the call is
due, before the shelf empties quietly.

* A catalog of samples with category and follow-up delay.
* Hand-outs with recipient, quantity and date.
* The follow-up date computed and stored on every hand-out.
* One state per unit: with the prospect, consumed or returned.
* One click to attach the order the sample turned into.
* A return stamped with the exact date it came back.
* One follow-up queue for everything still outside unpaid.
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
        'views/sample_item_0_views.xml',
        'views/sample_issue_1_views.xml',
        'views/sample_followup_2_views.xml',
        'views/menus.xml',
        'views/sample_followup_action.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
