# -*- coding: utf-8 -*-
{
    'name': 'ZoneBook',
    'version': '18.0.1.0.0',
    'summary': 'Define warehouse zones and storage rules and monitor occupancy so each zone is used as intended.',
    'description': '''ZoneBook - Zones Used As Planned
================================
Define warehouse zones and storage rules and monitor occupancy so each zone is used as intended.

Key points:
* Warehouse zones tracked in a dedicated register.
* Zone rules recorded with clear ownership and dates.
* Zone occupancy visible so nothing slips through.
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
        'views/warehouse_zone_entry_0_views.xml',
        'views/warehouse_zone_item_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
