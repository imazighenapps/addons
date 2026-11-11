# -*- coding: utf-8 -*-
{
    'name': 'PackStation',
    'version': '20.0.1.0.0',
    'summary': 'Manage packing stations with throughput and error tracking to balance load and improve shipping accuracy.',
    'description': '''PackStation - Packed Right, Packed Fast
=======================================
Manage packing stations with throughput and error tracking to balance load and improve shipping accuracy.

Key points:
* Pack stations tracked in a dedicated register.
* Station throughput recorded with clear ownership and dates.
* Pack errors visible so nothing slips through.
* Draft, confirmed and done states with an audit trail.
* Computed totals and counts kept up to date.
* Active flag to archive records no longer needed.
* Company-aware records for multi-company use.
* Mail chatter for notes and follow-up.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Inventory/Warehouse and Storage',
    'license': 'OPL-1',
    'price': 49.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.access.csv',
        'views/pack_station_entry_0_views.xml',
        'views/pack_station_item_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
