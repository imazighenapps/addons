# -*- coding: utf-8 -*-
{
    'name': 'HeadcountPlan',
    'version': '18.0.1.0.0',
    'summary': 'Plan headcount by department and period and compare approved positions with actual hires and vacancies.',
    'description': '''HeadcountPlan - Headcount Planned, Tracked
==========================================
Plan headcount by department and period and compare approved positions with actual hires and vacancies.

Key points:
* Headcount plan tracked in a dedicated register.
* Open positions recorded with clear ownership and dates.
* Plan vs actual visible so nothing slips through.
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
        'views/headcount_plan_entry_0_views.xml',
        'views/headcount_plan_item_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
