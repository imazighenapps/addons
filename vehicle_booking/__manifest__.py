# -*- coding: utf-8 -*-
{
    'name': 'VehicleBook',
    'version': '20.0.1.0.0',
    'summary': 'Reserve company vehicles with requester, time range and purpose, prevent overlapping bookings per vehicle, and track reservations through a clear workflow in a company-safe register.',
    'description': '''VehicleBook - Company Vehicle Reservation
=========================================
Shared company vehicles are hard to coordinate without a reservation system.
Employees request cars informally and conflicts surface at pickup time.

VehicleBook provides a vehicle catalogue and a booking register. Record who needs
which vehicle, when and why, and block overlapping confirmed reservations so the
schedule stays reliable.

* Vehicle catalogue with plate, seats and active flag.
* Bookings with requester, time range, destination and purpose.
* Overlap prevention for the same vehicle.
* States: draft, confirmed, done, cancelled.
* Search and reporting by vehicle, requester and period.
* Multi-company, no Enterprise dependency, no external Python package.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Services/Services',
    'license': 'OPL-1',
    'price': 49.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'hr',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.access.csv',
        'views/vehicle_booking_0_views.xml',
        'views/booking_vehicle_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
