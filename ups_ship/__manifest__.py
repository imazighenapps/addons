# -*- coding: utf-8 -*-
{
    'name': 'UPS Shipping',
    'version': '18.0.1.0.0',
    'summary': 'Création d’expéditions UPS, étiquettes/références de suivi et événements de livraison.',
    'description': '''UPS Shipping
============
Création d’expéditions UPS, étiquettes/références de suivi et événements de livraison.

UPS shipments are created in external portals without Odoo tracking.

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
        'views/ups_connection_0_views.xml',
        'views/ups_record_1_views.xml',
        'views/ups_log_2_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
