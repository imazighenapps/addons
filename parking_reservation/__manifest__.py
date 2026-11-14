# -*- coding: utf-8 -*-
{
    'name': 'ParkSpot',
    'version': '19.0.1.0.0',
    'summary': 'Manage parking spots and reservations with requester, time range and vehicle plate, prevent overlapping bookings per spot, and track availability in a company-safe register.',
    'description': '''ParkSpot - Parking Spot Reservation and Availability
===================================================
Limited parking creates daily friction when spots are assigned informally.
Conflicts and uncertainty waste time and cause complaints.

ParkSpot provides a parking spot catalogue and a reservation register. Define
spots, let employees reserve a time range and block overlapping confirmed
reservations so availability is clear and fair.

* Parking spots with code/name, location and active flag.
* Reservations with spot, requester, time range and vehicle plate.
* Overlap prevention for the same spot.
* States: draft, confirmed, cancelled.
* Search and reporting by spot, requester and period.
* Multi-company, no Enterprise dependency, no external Python package.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Productivity/Productivity',
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
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'views/parking_reservation_0_views.xml',
        'views/parking_spot_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
