# -*- coding: utf-8 -*-
{
    'name': 'FedEx Shipping',
    'version': '19.0.1.0.0',
    'summary': 'Gestion des envois FedEx, labels, tracking et exceptions de livraison.',
    'description': '''FedEx Shipping
==============
Gestion des envois FedEx, labels, tracking et exceptions de livraison.

FedEx shipments lack integrated tracking in Odoo deliveries.

* Connection profile with environment and token settings.
* Business records with status workflow and actions.
* Synchronisation/execution logs for traceability.
* Company-aware records and access control.
* No external Python dependency; operations modeled locally.
* Chatter tracking on key records.
* List/form/search views and dedicated menus.
* Seed/demo-friendly data for screenshots and testing.''',
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
        'views/fedex_connection_0_views.xml',
        'views/fedex_record_1_views.xml',
        'views/fedex_log_2_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
