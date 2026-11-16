# -*- coding: utf-8 -*-
{
    'name': 'TravelRequestLog',
    'version': '20.0.1.0.0',
    'summary': 'Record employee travel requests with dates, destination, purpose, estimated cost and approval states.',
    'description': '''TravelRequestLog - Employee Travel Request Register
===================================================
Travel requests handled by email lack visibility and consistent approvals.

TravelRequestLog provides a simple request and approval register for trips.

* Requests with employee, destination and travel dates.
* Purpose, estimated cost and notes.
* Approver and approval tracking.
* Draft, submitted, approved, completed and rejected states.
* Travel request history.
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
        'security/ir.access.csv',
        'data/sequence.xml',
        'views/travel_request_log_0_views.xml',
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
