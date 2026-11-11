# -*- coding: utf-8 -*-
{
    'name': 'TerritoryBook',
    'version': '18.0.1.0.0',
    'summary': 'Assign accounts to sales territories with clear rules and surface overlaps or customers left with no owner.',
    'description': '''TerritoryBook - No Account Left Orphaned
========================================
Assign accounts to sales territories with clear rules and surface overlaps or customers left with no owner.

Key points:
* Territories tracked in a dedicated register.
* Account mapping recorded with clear ownership and dates.
* Coverage gaps visible so nothing slips through.
* Draft, confirmed and done states with an audit trail.
* Computed totals and counts kept up to date.
* Active flag to archive records no longer needed.
* Company-aware records for multi-company use.
* Mail chatter for notes and follow-up.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'CRM/CRM',
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
        'views/territory_desk_entry_0_views.xml',
        'views/territory_desk_item_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
