# -*- coding: utf-8 -*-
{
    'name': 'OEEDesk',
    'version': '19.0.1.0.0',
    'summary': 'Compute OEE from stops, speed losses and rejects so each line sees where its effectiveness is really lost.',
    'description': '''OEEDesk - Effectiveness, Uncovered
==================================
Compute OEE from stops, speed losses and rejects so each line sees where its effectiveness is really lost.

Key points:
* Availability tracked in a dedicated register.
* Performance recorded with clear ownership and dates.
* Quality rate visible so nothing slips through.
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
    'price': 79.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'views/oee_desk_entry_0_views.xml',
        'views/oee_desk_item_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
