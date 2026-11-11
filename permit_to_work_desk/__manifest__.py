# -*- coding: utf-8 -*-
{
    'name': 'PermitDesk',
    'version': '19.0.1.0.0',
    'summary': 'Issue permits to work with hazard checklists and validity windows so risky jobs start only when cleared.',
    'description': '''PermitDesk - Risky Work, Cleared First
======================================
Issue permits to work with hazard checklists and validity windows so risky jobs start only when cleared.

Key points:
* Work permits tracked in a dedicated register.
* Hazard checks recorded with clear ownership and dates.
* Active permits visible so nothing slips through.
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
        'views/permit_to_entry_0_views.xml',
        'views/permit_to_item_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
