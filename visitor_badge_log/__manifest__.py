# -*- coding: utf-8 -*-
{
    'name': 'VisitorBadge',
    'version': '19.0.1.0.0',
    'summary': 'Register visitor badges and log issuance with visitor, host and times, track issued/returned/lost status, and keep a company-safe badge history.',
    'description': '''VisitorBadge - Visitor Badge Issuance Log
=========================================
Visitor badges tracked on paper are easy to lose track of. Reception needs to
know which badges are currently issued and which have not been returned.

VisitorBadge provides a badge catalogue and issuance records. Log who received a
badge, when, and from which host, then record returns or mark badges lost.

* Badge items with identifier and active flag.
* Issuance records with visitor, host and issue/return times.
* States: issued, returned, lost.
* Search and reporting by badge, visitor and state.
* Multi-company, no Enterprise dependency, no external Python package.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Services/Services',
    'license': 'OPL-1',
    'price': 39.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'hr',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'data/sequence.xml',
        'views/visitor_badge_issuance_0_views.xml',
        'views/visitor_badge_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
