# -*- coding: utf-8 -*-
{
    'name': 'ContractWatch',
    'version': '18.0.1.0.0',
    'summary': 'Track contract end and notice dates across vendors and customers so renewals never slip by unnoticed.',
    'description': '''ContractWatch - Renewals Never Missed
=====================================
Track contract end and notice dates across vendors and customers so renewals never slip by unnoticed.

Key points:
* Contracts tracked in a dedicated register.
* Notice dates recorded with clear ownership and dates.
* Renewal queue visible so nothing slips through.
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
        'views/contract_expiry_entry_0_views.xml',
        'views/contract_expiry_item_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
