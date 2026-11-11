# -*- coding: utf-8 -*-
{
    'name': 'MaintPlan',
    'version': '19.0.1.0.0',
    'summary': 'Schedule preventive maintenance by meter or calendar and keep overdue tasks visible before breakdowns happen.',
    'description': '''MaintPlan - Fixed Before It Breaks
==================================
Schedule preventive maintenance by meter or calendar and keep overdue tasks visible before breakdowns happen.

Key points:
* Preventive plans tracked in a dedicated register.
* Due tasks recorded with clear ownership and dates.
* Overdue work visible so nothing slips through.
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
        'views/maintenance_plan_entry_0_views.xml',
        'views/maintenance_plan_item_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
