# -*- coding: utf-8 -*-
{
    'name': 'SpareDesk',
    'version': '18.0.1.0.0',
    'summary': 'Maintain minimum levels for critical spare parts and link usage to the equipment that consumed them.',
    'description': '''SpareDesk - The Right Spare, In Stock
=====================================
Maintain minimum levels for critical spare parts and link usage to the equipment that consumed them.

Key points:
* Critical spares tracked in a dedicated register.
* Min levels recorded with clear ownership and dates.
* Spare usage visible so nothing slips through.
* Draft, confirmed and done states with an audit trail.
* Computed totals and counts kept up to date.
* Active flag to archive records no longer needed.
* Company-aware records for multi-company use.
* Mail chatter for notes and follow-up.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Operations/Operations',
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
        'views/spare_part_entry_0_views.xml',
        'views/spare_part_item_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
