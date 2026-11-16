# -*- coding: utf-8 -*-
{
    'name': 'FleetTireLog',
    'version': '18.0.1.0.0',
    'summary': 'Track tire fitting, rotation, replacement and removal with tread depth, odometer and cost.',
    'description': '''FleetTireLog - Fleet Tire Wear and Rotation Register
====================================================
Tire wear tracked in notebooks leads to late replacements and unplanned costs.

FleetTireLog provides a simple tire event register.

* Tire events with vehicle plate, brand and position.
* Event type: fitting, rotation, replacement, removal.
* Tread depth and odometer reading.
* Event date and unit cost.
* Draft, recorded, due and cancelled states.
* Multi-company, no Enterprise dependency, no external Python package.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Inventory/Inventory',
    'license': 'OPL-1',
    'price': 19.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
        'hr',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'data/sequence.xml',
        'views/fleet_tire_log_0_views.xml',
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
