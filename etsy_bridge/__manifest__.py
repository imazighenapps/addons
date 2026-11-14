# -*- coding: utf-8 -*-
{
    'name': 'Etsy Bridge',
    'version': '20.0.1.0.0',
    'summary': 'Connect Etsy shop to import orders, sync listing references and track fulfillment status from Odoo.',
    'description': '''Etsy Bridge - Sync Etsy listings and orders
===========================================
Artisans and merchants selling on Etsy need orders and fulfillment status
aligned with Odoo. Etsy Bridge provides shop connection, order records and
listing sync entries with statuses and logs.

* Etsy shop connection with credentials reference.
* Order import records with amounts and customer info.
* Listing sync entries (SKU, title, stock reference).
* Fulfillment lifecycle actions and tracking.
* Sync logs and error tracking.
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
        'views/etsy_connection_0_views.xml',
        'views/etsy_listing_1_views.xml',
        'views/etsy_order_2_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
