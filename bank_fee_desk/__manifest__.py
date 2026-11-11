# -*- coding: utf-8 -*-
{
    'name': 'BankFeeBook',
    'version': '18.0.1.0.0',
    'summary': 'Capture and categorize bank fees from statements so the real cost of banking is visible each month.',
    'description': '''BankFeeBook - Bank Costs, No Surprises
======================================
Capture and categorize bank fees from statements so the real cost of banking is visible each month.

Key points:
* Bank charges tracked in a dedicated register.
* Fee categories recorded with clear ownership and dates.
* Fee totals visible so nothing slips through.
* Draft, confirmed and done states with an audit trail.
* Computed totals and counts kept up to date.
* Active flag to archive records no longer needed.
* Company-aware records for multi-company use.
* Mail chatter for notes and follow-up.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Accounting/Accounting',
    'license': 'OPL-1',
    'price': 39.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'views/bank_fee_entry_0_views.xml',
        'views/bank_fee_item_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
