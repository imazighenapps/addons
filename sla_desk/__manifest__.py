# -*- coding: utf-8 -*-
{
    'name': 'SLADesk',
    'version': '18.0.1.0.0',
    'summary': 'Define service level targets per ticket type and track response and resolution breaches in real time.',
    'description': '''SLADesk - Promises Kept On Time
===============================
Define service level targets per ticket type and track response and resolution breaches in real time.

Key points:
* SLA policies tracked in a dedicated register.
* Response targets recorded with clear ownership and dates.
* Breaches visible so nothing slips through.
* Draft, confirmed and done states with an audit trail.
* Computed totals and counts kept up to date.
* Active flag to archive records no longer needed.
* Company-aware records for multi-company use.
* Mail chatter for notes and follow-up.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Services/Helpdesk',
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
        'views/sla_desk_entry_0_views.xml',
        'views/sla_desk_item_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
