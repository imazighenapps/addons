# -*- coding: utf-8 -*-
{
    'name': 'VendorRebate',
    'version': '18.0.1.0.0',
    'summary': 'Track supplier rebate agreements, accrue earnings on purchases and claim what the contract entitles you to.',
    'description': '''VendorRebate - Supplier Rebates Claimed
=======================================
Track supplier rebate agreements, accrue earnings on purchases and claim what the contract entitles you to.

Key points:
* Rebate agreements tracked in a dedicated register.
* Accrued rebates recorded with clear ownership and dates.
* Claimed amounts visible so nothing slips through.
* Draft, confirmed and done states with an audit trail.
* Computed totals and counts kept up to date.
* Active flag to archive records no longer needed.
* Company-aware records for multi-company use.
* Mail chatter for notes and follow-up.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Purchase/Purchase',
    'license': 'OPL-1',
    'price': 69.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'views/supplier_rebate_entry_0_views.xml',
        'views/supplier_rebate_item_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
