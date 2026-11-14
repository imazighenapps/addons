# -*- coding: utf-8 -*-
{
    'name': 'RoomBook',
    'version': '20.0.1.0.0',
    'summary': 'Manage meeting rooms and bookings with organizer, time range and attendees, prevent overlapping reservations for the same room, and view availability in a company-safe register.',
    'description': '''RoomBook - Meeting Room Booking and Availability
================================================
Shared meeting rooms get double-booked when reservations live in chats and
separate calendars. Teams waste time finding space and meetings start late.

RoomBook provides a simple room catalogue and a booking register. Define rooms
with capacity and location, record bookings with a time range and organizer, and
let the system block overlapping confirmed reservations so availability stays
reliable.

* Meeting rooms with capacity, location and active flag.
* Bookings with room, organizer, start/end, subject and attendees.
* Overlap prevention for the same room on confirmed bookings.
* States: draft, confirmed, cancelled.
* Search and reporting by room, organizer and period.
* Multi-company, no Enterprise dependency, no external Python package.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Productivity/Productivity',
    'license': 'OPL-1',
    'price': 49.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.access.csv',
        'views/meeting_booking_0_views.xml',
        'views/meeting_room_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
