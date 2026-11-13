# -*- coding: utf-8 -*-
{
    'name': 'Mondial Relay Shipping',
    'version': '18.0.1.0.0',
    'summary': 'Prepare Mondial Relay shipments, select relay points, generate label records and track parcel status from deliveries.',
    'description': '''Mondial Relay Shipping - Relay point shipping made simple
=========================================================
Shipping to relay points requires carrier-specific labels and tracking that
are often handled outside Odoo. This disconnect slows fulfillment and makes
parcel status hard to follow.

Mondial Relay Shipping adds a carrier connection, relay point selection and
shipment records linked to pickings. Users can prepare shipments, store
label references, tracking numbers and statuses, and keep a delivery log
for customer service.

* Carrier connection with merchant ID and environment.
* Relay point records (ID, name, address, country).
* Shipment linked to stock picking and customer.
* Label reference, tracking number and status lifecycle.
* Actions to prepare, generate label (record), mark shipped/delivered.
* Shipment event log for tracking updates.
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
        'views/mondialrelay_connection_0_views.xml',
        'views/mondialrelay_point_1_views.xml',
        'views/mondialrelay_shipment_2_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
