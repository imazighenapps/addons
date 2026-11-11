# -*- coding: utf-8 -*-
{
    'name': 'Deviation',
    'version': '20.0.1.0.0',
    'summary': 'Record every unplanned production deviation, judge its impact and close it with the approvals quality needs.',
    'description': '''Deviation - Deviations Closed For Real
======================================
Unplanned deviations surface on the shop floor, but the impact review
lives in an inbox and the approval that should close the file is
chased verbally. Without a single register, quality cannot prove what
happened, who assessed the risk, or which approval actually released
the batch.

Deviation records every production deviation with its area, product
and detected date, then drives a short review: the impact is judged,
an owner is assigned and the file moves through investigation to
approval. Each deviation can carry dedicated impact reviews so quality
keeps the reasoning, the risk level and the reviewer on the record.
The deviation closes only when the required approval is granted, and
the approval trail stays attached to the file.

* A register of production deviations with area, product and owner.
* Impact reviews with risk level, judgement and reviewer.
* A workflow from draft to investigation, approval and closure.
* Approvals recorded with decision, approver and date.
* Open deviations filtered for quality follow-up.
* Closure refused until an approval is granted.
* Stored counters for impact reviews and approvals.
* Multi-company isolation out of the box.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Operations/Operations',
    'license': 'OPL-1',
    'price': 69.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.access.csv',
        'views/devd_deviation_0_views.xml',
        'views/devd_impact_1_views.xml',
        'views/devd_approval_2_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
