# -*- coding: utf-8 -*-
{
    'name': 'SpendCap',
    'version': '19.0.1.0.0',
    'summary': 'Set purchasing budgets per category or project and warn buyers before a request commits spend over the cap.',
    'description': '''SpendCap - Spend Within The Cap
===============================
Set purchasing budgets per category or project and warn buyers before a request commits spend over the cap.

Key points:
* Spend budgets tracked in a dedicated register.
* Committed spend recorded with clear ownership and dates.
* Budget alerts visible so nothing slips through.
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
    'price': 59.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'views/purchase_budget_entry_0_views.xml',
        'views/purchase_budget_item_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
