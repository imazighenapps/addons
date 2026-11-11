# -*- coding: utf-8 -*-
{
    'name': 'ParcelWatch',
    'version': '20.0.1.0.0',
    'summary': 'Register the tracking number of every inbound parcel and one click to the carrier page, lost ones included.',
    'description': '''ParcelWatch - Tracking At One Click
===================================
Inbound parcels arrive with tracking numbers scattered across emails,
supplier portals and sticky notes. When a delivery is late, nobody knows
which carrier to call, which number to quote or whether the parcel was
ever marked as received. Lost boxes stay invisible until someone counts
the shelf and discovers the gap.

ParcelWatch keeps one register per inbound parcel: tracking number,
carrier, supplier and the dates you expect and receive it. A carrier
tracking link is computed from the number so one click opens the carrier
page, and a late flag is stored on every parcel that is still on the
road after its expected date. When the parcel arrives you stamp the
received date, and when it never shows up you mark it as lost with the
reason in the chatter. The late-parcels screen shows exactly which
boxes need a call today.

* A register of inbound parcels with tracking number and carrier.
* One-click carrier tracking link computed from the tracking number.
* Expected and received dates with a stored late flag.
* States for draft, in transit, received and lost.
* Received date stamped when the parcel arrives.
* Lost parcels kept with their reason in the chatter.
* Late parcels grouped for follow-up in one screen.
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
        'views/parcel_parcel_0_views.xml',
        'views/parcel_late_1_views.xml',
        'views/menus.xml',
        'data/ir_sequence_data.xml',
        'views/parcel_late_action.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
