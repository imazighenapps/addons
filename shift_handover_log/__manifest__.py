# -*- coding: utf-8 -*-
{
    'name': 'ShiftHandover',
    'version': '18.0.1.0.0',
    'summary': 'Record shift handovers with status summary, incidents and pending tasks, submit and acknowledge notes to preserve context across shifts in a company-safe register.',
    'description': '''ShiftHandover - Shift Handover and Notes Log
============================================
Shift handovers done verbally or on paper often lose critical context. Incoming
teams miss pending tasks and incidents, causing delays and repeated issues.

ShiftHandover provides a structured handover log. Record shift details, status,
incidents and pending actions, then submit and acknowledge the handover so
information is preserved and searchable.

* Handover records with date, shift, area and responsible persons.
* Status summary, incidents and pending tasks.
* States: draft, submitted, acknowledged.
* Search and reporting by shift, area and period.
* Multi-company, no Enterprise dependency, no external Python package.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Services/Services',
    'license': 'OPL-1',
    'price': 39.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'hr',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'data/sequence.xml',
        'views/shift_handover_log_0_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
