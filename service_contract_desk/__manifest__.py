# -*- coding: utf-8 -*-
{
    'name': 'ServiceContract',
    'version': '20.0.1.0.0',
    'summary': 'Manage service contracts with covered scope, response terms and renewal dates so commitments stay clear.',
    'description': '''ServiceContract - Service Promises On Record
============================================
Manage service contracts with covered scope, response terms and renewal dates so commitments stay clear.

Key points:
* Service contracts tracked in a dedicated register.
* Coverage terms recorded with clear ownership and dates.
* Renewal dates visible so nothing slips through.
* Draft, confirmed and done states with an audit trail.
* Computed totals and counts kept up to date.
* Active flag to archive records no longer needed.
* Company-aware records for multi-company use.
* Mail chatter for notes and follow-up.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Services/Services',
    'license': 'OPL-1',
    'price': 69.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.access.csv',
        'views/service_contract_entry_0_views.xml',
        'views/service_contract_item_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
