# -*- coding: utf-8 -*-
{
    'name': 'ContractorCheckin',
    'version': '20.0.1.0.0',
    'summary': 'Log contractor and external worker check-ins with company, host, purpose and timestamps, track on-site and checked-out status, and keep a company-safe presence register.',
    'description': '''ContractorCheckin - Contractor and External Worker Check-in Log
===============================================================
Paper sign-in sheets make it hard to know who is currently on-site and to
produce an audit trail of contractor visits.

ContractorCheckin provides a structured check-in log. Record contractor details,
host and purpose at arrival, capture check-out time on departure, and review
on-site presence and visit history.

* Check-in records with contractor name, company, host and purpose.
* Check-in and check-out timestamps.
* States: on-site, checked-out, cancelled.
* Search and reporting by company, host, date and state.
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
        'security/ir.access.csv',
        'data/sequence.xml',
        'views/contractor_checkin_0_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
