# -*- coding: utf-8 -*-
{
    'name': 'DockSlotPro - Delivery Time Slots and Capacity Planning',
    'version': '20.0.1.0.0',
    'summary': 'Plan weekly delivery windows with a capacity, book customers into a slot, close blackout days and stop the dock from being overloaded.',
    'description': '''DockSlotPro - Delivery Time Slots and Capacity Planning
========================================================
A delivery window is a promise. When three trucks arrive at the same dock at
the same time, the promise is broken before the customer reaches the gate.

DockSlotPro turns the loading dock into a bookable calendar. Define the
delivery windows of the week - Monday 08:00 to 12:00 at dock A, Thursday
14:00 to 18:00 at dock B - with the number of deliveries each window can
absorb. A booking links a customer, a date and a slot; the weekday of the
date must match the slot, and the slot refuses one booking more than its
capacity. Blackout days close the whole warehouse or a single dock for a
stocktake, a public holiday or a maintenance. The slot form shows how many
places are left for the next window, the booking keeps its full chatter
history, and every state change is one click: confirm, done, cancel or back
to draft.

* Weekly delivery windows per weekday, with start and end hour.
* Capacity per slot, enforced at confirmation time.
* Bookings linked to a customer, a date and a delivery reference.
* Weekday control: a Monday slot only accepts Monday dates.
* Blackout days for the whole warehouse or for a single slot.
* Places left for the next window, computed on confirmed bookings.
* Confirm, done, cancel and reset workflow with chatter.
* Multi-company, no Enterprise dependency.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'category': 'Inventory/Inventory',
    'license': 'OPL-1',
    'price': 59.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.access.csv',
        'data/sequence.xml',
        'views/dock_slot_0_views.xml',
        'views/dock_booking_1_views.xml',
        'views/dock_blackout_2_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
