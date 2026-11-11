# -*- coding: utf-8 -*-
{
    'name': 'NCDesk',
    'version': '20.0.1.0.0',
    'summary': 'Record nonconformances, analyze root causes and track corrective actions through to verified closure.',
    'description': '''NCDesk - Find It, Fix It, Prove It
==================================
Record nonconformances, analyze root causes and track corrective actions through to verified closure.

Key points:
* Nonconformances tracked in a dedicated register.
* Root cause recorded with clear ownership and dates.
* Corrective actions visible so nothing slips through.
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
    'price': 59.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.access.csv',
        'views/nonconformance_desk_entry_0_views.xml',
        'views/nonconformance_desk_item_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
