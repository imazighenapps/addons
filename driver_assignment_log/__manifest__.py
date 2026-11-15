# -*- coding: utf-8 -*-
{
    'name': 'DriverAssign',
    'version': '20.0.1.0.0',
    'summary': 'Track vehicle-to-driver assignments with start/end dates and status, keeping a clear current and historical record per vehicle and driver.',
    'description': '''DriverAssign - Vehicle Driver Assignment Log
============================================
Driver-to-vehicle assignments tracked informally or in spreadsheets create
confusion and responsibility disputes when records are outdated.

DriverAssign provides a structured assignment register. Link vehicles to drivers
with start/end dates and status, and keep current and past assignments visible.

* Assignments with vehicle, driver/employee and start/end dates.
* States: active, ended, cancelled.
* Notes and reason for assignment changes.
* Search and reporting by vehicle, driver and period.
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
        'fleet',
        'hr',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.access.csv',
        'data/sequence.xml',
        'views/driver_assignment_log_0_views.xml',
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
