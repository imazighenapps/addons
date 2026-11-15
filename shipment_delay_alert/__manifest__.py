# -*- coding: utf-8 -*-
{
    'name': 'LateShip',
    'version': '18.0.1.0.0',
    'summary': 'Detect outgoing transfers past their scheduled date, open one alert per late shipment and follow it through contact, resolution or dismissal.',
    'description': '''LateShip - Late Shipment Alert Desk
===================================
A late delivery discovered by the customer is already a complaint. Transfers
past their scheduled date sit in the same list as everything else, so nobody
sees them until the phone rings.

LateShip scans outgoing transfers against their scheduled date and opens a
follow-up alert per late shipment, with the delay in days and a clear status,
so the team calls the customer before the customer calls them.

* One alert per late outgoing transfer, with delay in days.
* Scan action with a reference date.
* States: open, contacted, resolved, dismissed.
* Customer, transfer and sales order kept on the alert.
* Chatter trail on each alert.
* No duplicate alert while one is still open for the same transfer.
* Multi-company, no Enterprise dependency, no external Python package.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Inventory/Inventory',
    'license': 'OPL-1',
    'price': 39.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'stock',
        'sale_stock',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'data/sequence.xml',
        'views/shipment_delay_alert_0_views.xml',
        'views/shipment_delay_scan_1_views.xml',
        'views/menus.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
