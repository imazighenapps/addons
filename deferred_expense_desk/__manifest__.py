# -*- coding: utf-8 -*-
{
    'name': 'DeferExpense',
    'version': '18.0.1.0.0',
    'summary': 'Spread prepaid expenses over their benefit period and recognize the cost month by month without manual journals.',
    'description': '''DeferExpense - Costs Spread, Not Spiked
=======================================
Spread prepaid expenses over their benefit period and recognize the cost month by month without manual journals.

Key points:
* Expense deferrals tracked in a dedicated register.
* Monthly recognition recorded with clear ownership and dates.
* Remaining balance visible so nothing slips through.
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
        'views/deferred_expense_entry_0_views.xml',
        'views/deferred_expense_item_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
