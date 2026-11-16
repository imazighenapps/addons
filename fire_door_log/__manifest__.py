# -*- coding: utf-8 -*-
{
    'name': 'FireDoorLog',
    'version': '20.0.1.0.0',
    'summary': 'Record fire door inspections with location, type, dates and hinge, seal, closer and gap results.',
    'description': '''FireDoorLog - Fire Door Inspection Register
===========================================
Fire door checks kept on paper leave defects and due dates hard to prove.

FireDoorLog provides a simple inspection register.

* Door records with reference, location and type.
* Inspection date and next inspection date.
* Hinge, seal, closer and gap check results.
* Responsible inspector and notes.
* Draft, passed, defect and cancelled states.
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
        'views/fire_door_log_0_views.xml',
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
