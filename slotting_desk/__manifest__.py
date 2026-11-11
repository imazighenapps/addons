# -*- coding: utf-8 -*-
{
    'name': 'SlotBook',
    'version': '20.0.1.0.0',
    'summary': 'Assign products to the right storage slots based on pick frequency and size to cut walking time in the warehouse.',
    'description': '''SlotBook - Every SKU In Its Place
=================================
Assign products to the right storage slots based on pick frequency and size to cut walking time in the warehouse.

Key points:
* Slot rules tracked in a dedicated register.
* Pick frequency recorded with clear ownership and dates.
* Relocation plan visible so nothing slips through.
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
        'views/slotting_desk_entry_0_views.xml',
        'views/slotting_desk_item_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
