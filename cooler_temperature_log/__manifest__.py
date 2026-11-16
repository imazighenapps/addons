# -*- coding: utf-8 -*-
{
    'name': 'CoolerTemperatureLog',
    'version': '20.0.1.0.0',
    'summary': 'Record cold storage temperatures with target range, automatic breach flag and states.',
    'description': '''CoolerTemperatureLog - Cold Storage Temperature Register
========================================================
Daily cold storage readings on paper hide breaches and missed checks.

CoolerTemperatureLog provides a simple temperature register.

* Readings with cooler name and location.
* Reading date/time and measured temperature.
* Configurable target minimum and maximum.
* Automatic in-range flag.
* Draft, recorded, breach and cancelled states.
* Multi-company, no Enterprise dependency, no external Python package.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Inventory/Inventory',
    'license': 'OPL-1',
    'price': 25.0,
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
        'views/cooler_temperature_log_0_views.xml',
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
