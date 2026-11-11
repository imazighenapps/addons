# -*- coding: utf-8 -*-
{
    'name': 'WarrantyDesk',
    'version': '18.0.1.0.0',
    'summary': 'Register warranty claims, verify coverage against the sale and track each claim to repair, replace or close.',
    'description': '''WarrantyDesk - Claims Covered And Closed
========================================
Register warranty claims, verify coverage against the sale and track each claim to repair, replace or close.

Key points:
* Warranty claims tracked in a dedicated register.
* Coverage check recorded with clear ownership and dates.
* Claim outcomes visible so nothing slips through.
* Draft, confirmed and done states with an audit trail.
* Computed totals and counts kept up to date.
* Active flag to archive records no longer needed.
* Company-aware records for multi-company use.
* Mail chatter for notes and follow-up.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Services/Services',
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
        'views/warranty_desk_entry_0_views.xml',
        'views/warranty_desk_item_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
