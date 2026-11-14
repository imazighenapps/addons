# -*- coding: utf-8 -*-
{
    'name': 'Trello Sync',
    'version': '19.0.1.0.0',
    'summary': 'Synchronisation cartes/listes Trello avec tâches et pipelines Odoo.',
    'description': '''Trello Sync
===========
Synchronisation cartes/listes Trello avec tâches et pipelines Odoo.

Trello cards are managed separately from Odoo tasks.

* Connection profile with environment and token settings.
* Business records with status workflow and actions.
* Synchronisation/execution logs for traceability.
* Company-aware records and access control.
* No external Python dependency; operations modeled locally.
* Chatter tracking on key records.
* List/form/search views and dedicated menus.
* Seed/demo-friendly data for screenshots and testing.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Productivity/Productivity',
    'license': 'OPL-1',
    'price': 79.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
        'project',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'views/trello_connection_0_views.xml',
        'views/trello_record_1_views.xml',
        'views/trello_log_2_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
