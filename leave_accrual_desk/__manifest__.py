# -*- coding: utf-8 -*-
{
    'name': 'LeaveBank',
    'version': '18.0.1.0.0',
    'summary': 'Accrue leave balances by rule and seniority and show every employee their earned, taken and remaining days.',
    'description': '''LeaveBank - Balances Earned Fairly
==================================
Accrue leave balances by rule and seniority and show every employee their earned, taken and remaining days.

Key points:
* Accrual rules tracked in a dedicated register.
* Leave balances recorded with clear ownership and dates.
* Balance history visible so nothing slips through.
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
    'price': 59.0,
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
        'views/leave_accrual_entry_0_views.xml',
        'views/leave_accrual_item_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
