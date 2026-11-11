# -*- coding: utf-8 -*-
{
    'name': 'ActivitySLA',
    'version': '18.0.1.0.0',
    'summary': 'Set response-time targets for lead activities and flag the follow-ups that breach the SLA before they go cold.',
    'description': '''ActivitySLA - Replies Before They Cool
======================================
Set response-time targets for lead activities and flag the follow-ups that breach the SLA before they go cold.

Key points:
* Response targets tracked in a dedicated register.
* Overdue follow-ups recorded with clear ownership and dates.
* Team compliance visible so nothing slips through.
* Draft, confirmed and done states with an audit trail.
* Computed totals and counts kept up to date.
* Active flag to archive records no longer needed.
* Company-aware records for multi-company use.
* Mail chatter for notes and follow-up.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'CRM/CRM',
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
        'views/activity_sla_entry_0_views.xml',
        'views/activity_sla_item_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
