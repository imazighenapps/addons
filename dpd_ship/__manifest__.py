# -*- coding: utf-8 -*-
{
    'name': 'DPD Shipping',
    'version': '19.0.1.0.0',
    'summary': 'Create DPD shipments, labels and tracking records from deliveries and monitor parcel status in Odoo.',
    'description': '''DPD Shipping - DPD parcel shipping from Odoo
============================================
DPD parcel shipments managed in external portals are hard to track alongside
Odoo deliveries. This module provides DPD connection settings, shipment
records, label/tracking references and a delivery status lifecycle.

* DPD connection with depot/customer number and environment.
* Shipments linked to pickings and recipients.
* Label and tracking references, weight and parcel count.
* States: draft, ready, label, in_transit, delivered, exception.
* Tracking event log.
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
        'views/dpd_connection_0_views.xml',
        'views/dpd_shipment_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
