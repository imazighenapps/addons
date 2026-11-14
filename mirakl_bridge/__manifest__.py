# -*- coding: utf-8 -*-
{
    'name': 'Mirakl Bridge',
    'version': '19.0.1.0.0',
    'summary': 'Connect to Mirakl marketplaces to import orders, track shipments and synchronize order status with Odoo.',
    'description': '''Mirakl Bridge - Import Mirakl marketplace orders
================================================
Selling on Mirakl-powered marketplaces requires importing orders and
updating shipment statuses. Doing this manually is slow and error-prone.

Mirakl Bridge provides connection profiles, order import records and
shipment updates with statuses and logs, giving operations teams a clear
view of marketplace orders inside Odoo.

* Marketplace connection with shop ID and API key reference.
* Imported order records with lines summary and amounts.
* Shipment/status updates and tracking info.
* Order lifecycle: new, accepted, shipped, invoiced, closed, error.
* Sync log history.
* No external Python dependency.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Sales/Sales',
    'license': 'OPL-1',
    'price': 149.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
        'sale',
        'stock',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'data/sequence.xml',
        'views/mirakl_connection_0_views.xml',
        'views/mirakl_order_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
