# -*- coding: utf-8 -*-
{
    'name': 'IdeaDesk',
    'version': '19.0.1.0.0',
    'summary': 'Give employees one place to post improvement ideas, evaluate them fairly and credit the ones implemented.',
    'description': '''IdeaDesk - Ideas That Land
==========================
Good improvement ideas are raised in hallways, written on sticky notes
or dropped into a suggestion box nobody opens on time. Some are never
reviewed, some are implemented without credit, and the people who spot
waste stop bothering to speak up because nothing visible ever happens.

IdeaDesk keeps one Odoo board per idea: the author, the area it
improves, the expected gain and the date it was submitted. Each idea
moves through a simple evaluation flow from submitted to accepted or
rejected, and implemented ideas are stamped with the date they went
live. Review notes record the decision in plain words, and the open-
ideas screen shows everything still waiting for an answer. When an idea
lands, the credit and the history stay on the same record.

* A register of improvement ideas with author, area and expected gain.
* A simple flow from submitted to evaluated, accepted or rejected.
* Implemented ideas stamped with the date they went live.
* Review notes captured on every evaluation for a clear decision trail.
* One open-ideas screen for everything still waiting for an answer.
* A negative expected gain is refused for you.
* An implemented idea must be accepted before it is marked done.
* Multi-company isolation out of the box.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Operations/Operations',
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
        'views/idea_proposal_0_views.xml',
        'views/idea_review_1_views.xml',
        'views/idea_open_2_views.xml',
        'views/menus.xml',
        'views/idea_open_action.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
