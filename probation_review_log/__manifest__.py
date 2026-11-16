# -*- coding: utf-8 -*-
{
    'name': 'ProbationReviewLog',
    'version': '19.0.1.0.0',
    'summary': 'Document employee probation periods, review dates, scores and confirmation decisions.',
    'description': '''ProbationReviewLog - Employee Probation Review Register
=======================================================
Probation end dates kept in calendars lead to missed reviews and undocumented
decisions.

ProbationReviewLog provides a simple probation review register.

* Reviews with employee, reviewer and probation period dates.
* Review date and 0-100 score.
* Decision: pending, passed, extended or failed.
* Draft, submitted, closed and cancelled states.
* History of probation reviews per employee.
* Multi-company, no Enterprise dependency, no external Python package.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Human Resources/Employees',
    'license': 'OPL-1',
    'price': 29.0,
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
        'views/probation_review_log_0_views.xml',
        'views/menus.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
