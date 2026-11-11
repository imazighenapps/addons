# -*- coding: utf-8 -*-
{
    'name': 'ProjectCost',
    'version': '19.0.1.0.0',
    'summary': 'Track planned versus actual cost on each project and forecast the margin before the overrun surprises you.',
    'description': '''ProjectCost - Margins Seen In Time
==================================
Track planned versus actual cost on each project and forecast the margin before the overrun surprises you.

Key points:
* Project budgets tracked in a dedicated register.
* Cost vs budget recorded with clear ownership and dates.
* Margin forecast visible so nothing slips through.
* Draft, confirmed and done states with an audit trail.
* Computed totals and counts kept up to date.
* Active flag to archive records no longer needed.
* Company-aware records for multi-company use.
* Mail chatter for notes and follow-up.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Services/Project',
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
        'views/project_budget_entry_0_views.xml',
        'views/project_budget_item_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
