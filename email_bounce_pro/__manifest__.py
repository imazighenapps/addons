# -*- coding: utf-8 -*-
{
    'name': 'BounceGuard',
    'version': '20.0.1.0.0',
    'summary': 'Read the bounce notifications Odoo already receives, keep a dated register of every rejected address, and flag the customers whose email keeps failing.',
    'description': '''BounceGuard - Bad Addresses Caught Early
========================================
Odoo sends the confirmation, receives the delivery failure in its postmaster
mailbox, marks the notification as bounced and waits. Meanwhile every
reminder, portal invitation and promotion that needs one address keeps
failing, because the ten failures are spread across ten mail threads nobody
reads.

BounceGuard turns those silent failures into a register of its own. A one
click scan reads the bounced notifications, records one event per address
with the date, the reason and the linked message, and a second scan never
duplicates what is already filed. When a customer accumulates more failures
than the threshold of a rule, its record is flagged: the next campaign skips
it until somebody fixes the address and clears the flag.

* One dated event per bounced notification.
* Contact, address, reason and message kept together.
* Replays never duplicate an already filed bounce.
* Threshold rule per company, with its owner notified.
* Customers flagged as soon as the threshold is crossed.
* Handle, ignore and reopen each event.
* Counts directly visible on every partner form.
* Company isolation and state filters.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Marketing/Marketing',
    'license': 'OPL-1',
    'price': 99.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.access.csv',
        'views/bounce_event_0_views.xml',
        'views/bounce_guard_rule_1_views.xml',
        'views/bounce_scan_wizard_2_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
