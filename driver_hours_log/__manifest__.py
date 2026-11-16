# -*- coding: utf-8 -*-
{
    'name': 'DriverHoursLog',
    'version': '18.0.1.0.0',
    'summary': 'Record daily driver duty with driving and break minutes, limit and automatic exceedance flag.',
    'description': '''DriverHoursLog - Driver Duty and Driving Hours Register
=======================================================
Driving hours checked after the fact make daily limits and breaks hard to
enforce.

DriverHoursLog provides a simple duty register.

* Duty records with driver, vehicle and date.
* Driving minutes and break minutes.
* Configurable daily limit with automatic exceedance flag.
* Responsible user and notes.
* Draft, validated, alert and cancelled states.
* Multi-company, no Enterprise dependency, no external Python package.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Inventory/Inventory',
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
        'views/driver_hours_log_0_views.xml',
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
