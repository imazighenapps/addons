# -*- coding: utf-8 -*-
{
    'name': 'EquipLog',
    'version': '18.0.1.0.0',
    'summary': "Keep an equipment register with usage and service history so each asset's condition is known at a glance.",
    'description': '''EquipLog - Every Asset's Story
==============================
Keep an equipment register with usage and service history so each asset's condition is known at a glance.

Key points:
* Equipment register tracked in a dedicated register.
* Usage log recorded with clear ownership and dates.
* Service history visible so nothing slips through.
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
        'views/equipment_log_entry_0_views.xml',
        'views/equipment_log_item_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
