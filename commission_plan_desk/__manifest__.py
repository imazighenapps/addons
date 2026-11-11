# -*- coding: utf-8 -*-
{
    'name': 'CommissionBook',
    'version': '20.0.1.0.0',
    'summary': 'Accrue sales commissions per rep and rule on confirmed invoices and prepare the payout list without spreadsheets.',
    'description': '''CommissionBook - Commissions Counted Right
==========================================
Accrue sales commissions per rep and rule on confirmed invoices and prepare the payout list without spreadsheets.

Key points:
* Commission rules tracked in a dedicated register.
* Accrued amounts recorded with clear ownership and dates.
* Payout lines visible so nothing slips through.
* Draft, confirmed and done states with an audit trail.
* Computed totals and counts kept up to date.
* Active flag to archive records no longer needed.
* Company-aware records for multi-company use.
* Mail chatter for notes and follow-up.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Sales/Sales',
    'license': 'OPL-1',
    'price': 79.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.access.csv',
        'views/commission_plan_entry_0_views.xml',
        'views/commission_plan_item_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
