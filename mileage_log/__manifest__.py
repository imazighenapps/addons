# -*- coding: utf-8 -*-
{
    'name': 'MileageLog',
    'version': '20.0.1.0.0',
    'summary': 'Log business trips with distance, purpose and rate, compute reimbursable amounts, validate entries, and report mileage by employee and period in a company-safe register.',
    'description': '''MileageLog - Business Mileage and Trip Log
==========================================
Mileage claimed from memory or ad-hoc notes is error-prone and hard to validate.
Finance teams spend time reconciling distances and amounts.

MileageLog provides a structured trip log. Record date, route, purpose, distance
and rate per trip, compute the reimbursable amount and validate entries for
consistent reporting and reimbursement.

* Trip entries with employee, date, route and purpose.
* Distance, rate and computed amount.
* States: draft, submitted, validated, refused.
* Search and reporting by employee, state and period.
* Multi-company, no Enterprise dependency, no external Python package.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Human Resources/Employee',
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
        'security/ir.access.csv',
        'data/sequence.xml',
        'views/mileage_log_0_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
