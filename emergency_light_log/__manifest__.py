# -*- coding: utf-8 -*-
{
    'name': 'EmergencyLightLog',
    'version': '20.0.1.0.0',
    'summary': 'Record emergency lighting tests with location, type, duration, battery and lamp results.',
    'description': '''EmergencyLightLog - Emergency Lighting Test Register
====================================================
Emergency lighting tests kept on paper make failures and due dates hard to
prove.

EmergencyLightLog provides a simple test register.

* Light records with reference, location and type.
* Test date, next test date and duration.
* Battery and lamp result flags.
* Responsible tester and notes.
* Draft, tested, failed and cancelled states.
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
        'views/emergency_light_log_0_views.xml',
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
