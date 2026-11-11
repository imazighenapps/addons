# -*- coding: utf-8 -*-
{
    'name': 'ROPWatch',
    'version': '19.0.1.0.0',
    'summary': 'Review and tune reorder points per product with demand history and raise alerts before a stockout happens.',
    'description': '''ROPWatch - Stockouts Seen Coming
================================
Review and tune reorder points per product with demand history and raise alerts before a stockout happens.

Key points:
* Reorder points tracked in a dedicated register.
* Stock alerts recorded with clear ownership and dates.
* Suggested qty visible so nothing slips through.
* Draft, confirmed and done states with an audit trail.
* Computed totals and counts kept up to date.
* Active flag to archive records no longer needed.
* Company-aware records for multi-company use.
* Mail chatter for notes and follow-up.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Inventory/Inventory',
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
        'views/reorder_point_entry_0_views.xml',
        'views/reorder_point_item_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
