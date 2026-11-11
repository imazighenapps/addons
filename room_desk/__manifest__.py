# -*- coding: utf-8 -*-
{
    'name': 'RoomBook',
    'version': '20.0.1.0.0',
    'summary': 'Book the meeting rooms without the double-booking drama, with capacity, equipment and a clean conflict rule.',
    'description': '''RoomBook - No Double Booking, Ever
==================================
Meeting rooms are promised in chat threads, pencilled in a shared
calendar nobody trusts and fought over when two teams arrive at the
same door. Capacity is guessed, the projector is missing and there is
no record of who actually booked the room.

RoomBook keeps one register per room with its location, its capacity
and the equipment it offers. Every booking names the room, the host,
the subject and the exact start and end, and a conflict rule refuses
any booking that overlaps another confirmed reservation in the same
room. Cancellations stay on record, the agenda stays readable, and the
reception desk can answer with one screen instead of three apologies.

* A register of meeting rooms with location, capacity and equipment.
* Bookings with host, subject, attendees and exact start and end.
* A conflict rule that refuses overlapping bookings in the same room.
* Draft, confirmed and cancelled states with a full chatter trail.
* Room and upcoming booking counters kept up to date on each room.
* A clean agenda view grouped by room and by day.
* Multi-company isolation out of the box.
* No calendar integration required: the room book is the source of truth.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Operations/Operations',
    'license': 'OPL-1',
    'price': 39.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.access.csv',
        'views/room_room_0_views.xml',
        'views/room_booking_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
