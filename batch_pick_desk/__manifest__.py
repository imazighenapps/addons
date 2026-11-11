# -*- coding: utf-8 -*-
{
    'name': 'BatchPick',
    'version': '20.0.1.0.0',
    'summary': 'Group compatible pickings into waves so operators pick once for many orders and finish rounds faster.',
    'description': '''BatchPick - Pick Once, Ship Many
================================
Group compatible pickings into waves so operators pick once for many orders and finish rounds faster.

Key points:
* Pick waves tracked in a dedicated register.
* Grouped picks recorded with clear ownership and dates.
* Pick progress visible so nothing slips through.
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
        'views/batch_pick_entry_0_views.xml',
        'views/batch_pick_item_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
