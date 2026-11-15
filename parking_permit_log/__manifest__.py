# -*- coding: utf-8 -*-
{
    'name': 'ParkingPermitLog',
    'version': '20.0.1.0.0',
    'summary': 'Register parking permits with holder, vehicle, zone/spot and validity dates, tracking active, expired and cancelled authorizations.',
    'description': '''ParkingPermitLog - Parking Permit Register
==========================================
Sites with limited parking often track permits informally, making it unclear
who is authorized and when permits expire.

ParkingPermitLog keeps a simple register of permits with validity tracking.

* Permit records with holder, vehicle plate and zone/spot.
* Start and expiry dates and responsible issuer.
* Permit type and notes.
* Draft, active, expired and cancelled states.
* Search and filters by state and dates.
* Multi-company, no Enterprise dependency, no external Python package.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Services/Project',
    'license': 'OPL-1',
    'price': 19.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'hr',
        'contacts',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.access.csv',
        'data/sequence.xml',
        'views/parking_permit_log_0_views.xml',
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
