# -*- coding: utf-8 -*-
{
    'name': 'TravelRequest',
    'version': '19.0.1.0.0',
    'summary': 'Submit and approve employee business travel requests with destination, dates, purpose and estimated cost, tracked through a company-safe approval workflow.',
    'description': '''TravelRequest - Employee Business Travel Request
================================================
Business travel arranged informally lacks prior approval and cost visibility.
Managers discover trips late and finance cannot anticipate expenses.

TravelRequest provides a structured pre-trip request. Employees submit destination,
dates, purpose and estimated costs; managers approve or refuse so travel is planned
and traceable.

* Requests with employee, destination, dates and purpose.
* Estimated cost and transport/accommodation notes.
* States: draft, submitted, approved, refused, done.
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
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'data/sequence.xml',
        'views/travel_request_0_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
