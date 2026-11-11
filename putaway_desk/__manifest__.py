# -*- coding: utf-8 -*-
{
    'name': 'PutawayDesk',
    'version': '19.0.1.0.0',
    'summary': 'Guide receipts to the right bin with simple putaway rules and keep a log of where every pallet landed.',
    'description': '''PutawayDesk - Receipts To The Right Bin
=======================================
Guide receipts to the right bin with simple putaway rules and keep a log of where every pallet landed.

Key points:
* Putaway rules tracked in a dedicated register.
* Suggested bins recorded with clear ownership and dates.
* Putaway log visible so nothing slips through.
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
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'views/putaway_desk_entry_0_views.xml',
        'views/putaway_desk_item_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
