# -*- coding: utf-8 -*-
{
    'name': 'OverstockWatch',
    'version': '18.0.1.0.0',
    'summary': 'Flag overstocked and slow-moving items with their carrying cost and suggest actions to free the cash.',
    'description': '''OverstockWatch - Cash Freed From Shelves
========================================
Flag overstocked and slow-moving items with their carrying cost and suggest actions to free the cash.

Key points:
* Slow movers tracked in a dedicated register.
* Excess stock recorded with clear ownership and dates.
* Action list visible so nothing slips through.
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
        'views/overstock_desk_entry_0_views.xml',
        'views/overstock_desk_item_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
