# -*- coding: utf-8 -*-
{
    'name': 'RSVPDesk',
    'version': '20.0.1.0.0',
    'summary': 'Manage event invitations and RSVPs with reminders and a clean attendance list on the day of the event.',
    'description': '''RSVPDesk - Every Seat Accounted For
===================================
Manage event invitations and RSVPs with reminders and a clean attendance list on the day of the event.

Key points:
* Invitations tracked in a dedicated register.
* RSVP status recorded with clear ownership and dates.
* Attendance list visible so nothing slips through.
* Draft, confirmed and done states with an audit trail.
* Computed totals and counts kept up to date.
* Active flag to archive records no longer needed.
* Company-aware records for multi-company use.
* Mail chatter for notes and follow-up.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Marketing/Marketing',
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
        'views/event_rsvp_entry_0_views.xml',
        'views/event_rsvp_item_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
