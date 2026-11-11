# -*- coding: utf-8 -*-
{
    'name': 'ReserveDesk',
    'version': '18.0.1.0.0',
    'summary': 'Reserve stock for priority orders or projects and release it explicitly when plans change.',
    'description': '''ReserveDesk - Reserved Means Reserved
=====================================
Reserve stock for priority orders or projects and release it explicitly when plans change.

Key points:
* Reservations tracked in a dedicated register.
* Reserved for recorded with clear ownership and dates.
* Release queue visible so nothing slips through.
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
    'price': 59.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'views/stock_reserve_entry_0_views.xml',
        'views/stock_reserve_item_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
