# -*- coding: utf-8 -*-
{
    'name': 'DisposalDesk',
    'version': '19.0.1.0.0',
    'summary': 'Record fixed asset disposals and sales, compute the gain or loss and post the closing entries cleanly.',
    'description': '''DisposalDesk - Disposals Closed Cleanly
=======================================
Record fixed asset disposals and sales, compute the gain or loss and post the closing entries cleanly.

Key points:
* Disposals tracked in a dedicated register.
* Gain or loss recorded with clear ownership and dates.
* Disposal entries visible so nothing slips through.
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
        'views/asset_disposal_entry_0_views.xml',
        'views/asset_disposal_item_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
