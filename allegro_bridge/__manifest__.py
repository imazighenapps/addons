# -*- coding: utf-8 -*-
{
    'name': 'Allegro Bridge',
    'version': '20.0.1.0.0',
    'summary': 'Connect Allegro marketplace to import orders, manage offers and track fulfillment status in Odoo.',
    'description': '''Allegro Bridge - Sell and fulfill on Allegro from Odoo
======================================================
Merchants selling on Allegro need orders and offer status synchronized
with Odoo operations. Allegro Bridge provides connection settings, offer
records and imported orders with fulfillment tracking.

* Allegro account connection with credentials reference.
* Offer records (price, stock, status).
* Imported orders with amounts and shipping details.
* Fulfillment lifecycle actions and logs.
* No external Python dependency.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Sales/Sales',
    'license': 'OPL-1',
    'price': 99.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
        'sale',
        'stock',
    ],
    'data': [
        'security/security.xml',
        'security/ir.access.csv',
        'data/sequence.xml',
        'views/allegro_connection_0_views.xml',
        'views/allegro_offer_1_views.xml',
        'views/allegro_order_2_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
