# -*- coding: utf-8 -*-
{
    'name': 'LockerAssign',
    'version': '20.0.1.0.0',
    'summary': 'Manage lockers and assign them to employees with issue and return dates, track assigned and returned states, and keep a company-safe assignment history.',
    'description': '''LockerAssign - Employee Locker Assignment Tracking
=================================================
Locker assignments maintained on spreadsheets or boards quickly become outdated,
making it unclear who holds which locker and which lockers are available.

LockerAssign provides a locker catalogue and assignment records. Assign a locker
to an employee, record issue and return dates, and keep a clear history of
current and past holders.

* Locker catalogue with identifier and location.
* Assignments linking locker to employee with dates.
* States: assigned, returned.
* Search and reporting by locker, employee and state.
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
        'views/locker_assignment_0_views.xml',
        'views/locker_locker_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
