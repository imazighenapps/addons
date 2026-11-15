# -*- coding: utf-8 -*-
{
    'name': 'FuelCardAssign',
    'version': '20.0.1.0.0',
    'summary': 'Register fuel cards and assign them to employees with issue and return dates, track assigned/returned/blocked status, and keep a company-safe holder history.',
    'description': '''FuelCardAssign - Fuel Card Assignment and Tracking
==================================================
Fuel cards issued to drivers are often tracked in spreadsheets, making it hard
to know who holds each card and when it was returned or blocked.

FuelCardAssign provides a card catalogue and assignment records. Issue a card to
an employee, record returns or block the assignment so holder history stays clear.

* Fuel cards with identifier, provider and active flag.
* Assignments per employee with issue and return dates.
* States: assigned, returned, blocked.
* Search and reporting by card, employee and state.
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
        'views/fuel_card_assignment_0_views.xml',
        'views/fuel_card_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
