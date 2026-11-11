# -*- coding: utf-8 -*-
{
    'name': 'CrossDock',
    'version': '20.0.1.0.0',
    'summary': 'Route eligible receipts straight to outgoing orders and bypass storage for the goods that should never sit.',
    'description': '''CrossDock - In, Out, No Storage
===============================
Route eligible receipts straight to outgoing orders and bypass storage for the goods that should never sit.

Key points:
* Inbound to outbound tracked in a dedicated register.
* Cross-dock queue recorded with clear ownership and dates.
* Bypassed storage visible so nothing slips through.
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
    'price': 59.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.access.csv',
        'views/cross_dock_entry_0_views.xml',
        'views/cross_dock_item_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
