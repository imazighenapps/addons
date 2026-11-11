# -*- coding: utf-8 -*-
{
    'name': 'ExpenseGuard',
    'version': '18.0.1.0.0',
    'summary': 'Enforce expense policies by category and limit and flag claims that break the rules before approval.',
    'description': '''ExpenseGuard - Claims Inside The Rules
======================================
Enforce expense policies by category and limit and flag claims that break the rules before approval.

Key points:
* Expense rules tracked in a dedicated register.
* Policy breaches recorded with clear ownership and dates.
* Approved claims visible so nothing slips through.
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
    'price': 49.0,
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
        'views/expense_policy_entry_0_views.xml',
        'views/expense_policy_item_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
