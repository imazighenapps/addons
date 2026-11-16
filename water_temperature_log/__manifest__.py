# -*- coding: utf-8 -*-
{
    'name': 'WaterTemperatureLog',
    'version': '20.0.1.0.0',
    'summary': 'Record water temperature readings per point with target range, automatic flag and alerts.',
    'description': '''WaterTemperatureLog - Water Temperature Monitoring Register
===========================================================
Water temperature readings kept on paper hide out-of-range points and missed
checks.

WaterTemperatureLog provides a simple monitoring register.

* Points with name and type (tap, shower, tank, boiler).
* Reading date and measured temperature.
* Configurable target minimum and maximum.
* Automatic in-range flag.
* Draft, recorded, alert and cancelled states.
* Multi-company, no Enterprise dependency, no external Python package.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Services/Project',
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
        'views/water_temperature_log_0_views.xml',
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
