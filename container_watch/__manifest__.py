# -*- coding: utf-8 -*-
{
    'name': 'ContainerWatch',
    'version': '20.0.1.0.0',
    'summary': 'Follow your import containers from booking to warehouse with the ETA, the charges and who owes what.',
    'description': '''ContainerWatch - Containers Without Surprises
============================================
Import containers travel for weeks with their ETA changing, charges
piling up and nobody sure who owes the demurrage or the release fee.
Booking references live in emails, the forwarder calls with a new date,
and the warehouse hears about the arrival only when the truck is at the
gate.

ContainerWatch keeps one record per container: booking, vessel, origin
and destination, with the planned and actual arrival dates. Every charge
is listed with its type, amount and the party who owes it, and the
totals tell you what the container really costs before it reaches the
dock. States move the container from booked to released, the actual
arrival is stamped on release, and a delay flag is stored when the ETA
slips past today. The team sees which containers are late and which
charges are still unsettled in one place.

* One record per container with booking, vessel and route.
* Planned and actual arrival dates with a stored delay flag.
* Charges with type, amount and the party who owes them.
* Totals per container for a clear landed cost view.
* States from booked to at sea, arrived and released.
* Actual arrival stamped when the container is released.
* Unsettled charges visible at a glance.
* Multi-company isolation out of the box.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Inventory/Warehouse and Storage',
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
        'views/container_shipment_0_views.xml',
        'views/container_charge_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
