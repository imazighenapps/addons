# -*- coding: utf-8 -*-
{
    'name': 'FXExposure',
    'version': '19.0.1.0.0',
    'summary': 'Monitor foreign-currency exposure from open receivables and payables and record hedging decisions.',
    'description': '''FXExposure - Currency Risk In Sight
===================================
Monitor foreign-currency exposure from open receivables and payables and record hedging decisions.

Key points:
* Foreign balances tracked in a dedicated register.
* Exposure by currency recorded with clear ownership and dates.
* Hedge notes visible so nothing slips through.
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
        'views/fx_exposure_entry_0_views.xml',
        'views/fx_exposure_item_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
