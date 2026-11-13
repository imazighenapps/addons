# -*- coding: utf-8 -*-
{
    'name': 'Colissimo Shipping',
    'version': '19.0.1.0.0',
    'summary': 'Prepare Colissimo parcels, generate label records and tracking numbers, and follow delivery statuses from your pickings.',
    'description': '''Colissimo Shipping - Ship with Colissimo from Odoo
==================================================
French shippers using Colissimo need labels, tracking and delivery status
visible inside Odoo. Manual carrier portals create double entry and poor
customer visibility.

Colissimo Shipping provides a connection profile, shipment records linked to
deliveries, and a simple lifecycle: prepare, create label, ship, deliver.
Tracking numbers, label references, options (signature, relay/home) and
event logs are stored for support and reporting.

* Connection with contract number and environment.
* Shipments linked to stock pickings and customers.
* Service options (home, relay, signature).
* Label/tracking generation records and status tracking.
* Event history and exception handling.
* No external Python dependency.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Inventory/Delivery',
    'license': 'OPL-1',
    'price': 79.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
        'stock',
        'delivery',
        'sale',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'data/sequence.xml',
        'views/colissimo_connection_0_views.xml',
        'views/colissimo_shipment_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
