# -*- coding: utf-8 -*-
{
    'name': 'ShiftSwap',
    'version': '18.0.1.0.0',
    'summary': 'Let employees request shift swaps with a manager approval so the roster stays covered and agreed.',
    'description': '''ShiftSwap - Swaps Agreed, Roster Safe
=====================================
Let employees request shift swaps with a manager approval so the roster stays covered and agreed.

Key points:
* Swap requests tracked in a dedicated register.
* Approvals recorded with clear ownership and dates.
* Updated roster visible so nothing slips through.
* Draft, confirmed and done states with an audit trail.
* Computed totals and counts kept up to date.
* Active flag to archive records no longer needed.
* Company-aware records for multi-company use.
* Mail chatter for notes and follow-up.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Human Resources/Employee',
    'license': 'OPL-1',
    'price': 39.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
        'hr',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'views/shift_swap_entry_0_views.xml',
        'views/shift_swap_item_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
