# -*- coding: utf-8 -*-
{
    'name': 'YardWatch',
    'version': '20.0.1.0.0',
    'summary': 'Know which trailer stands where in your yard, how long it has been waiting and when the dock must absorb it.',
    'description': '''YardWatch - A Yard That Runs Itself
===================================
Trailers arrive all morning, park wherever there is room and wait for a
dock that never seems to be ready. The yard board lives on a whiteboard
by the gate: nobody knows how long a trailer has been standing, which
slot is free, or which delivery is putting pressure on the dock right
now.

YardWatch gives the yard a live register in Odoo. Declare every slot
with its dock and its capacity, log each trailer as it arrives with its
carrier and the slot it occupies, and move it through waiting, docked
and departed states as the day unfolds. Waiting time is computed from
the arrival, so the longest queues are visible at a glance. When a
trailer leaves, the departure is stamped and the slot is free again.
The pressure on the dock is the list you already needed, not a phone
call to the gate.

* A register of yard slots with dock, capacity and status.
* Trailer arrivals logged with carrier, reference and arrival time.
* Waiting, docked and departed states with dated transitions.
* Waiting duration computed and stored on every trailer.
* Departure stamped with the exact time the trailer left the yard.
* One screen to see which trailer stands where right now.
* Slot capacity and occupancy kept under control.
* Multi-company isolation out of the box.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Inventory/Warehouse and Storage',
    'license': 'OPL-1',
    'price': 45.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.access.csv',
        'views/yard_slot_0_views.xml',
        'views/yard_trailer_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
