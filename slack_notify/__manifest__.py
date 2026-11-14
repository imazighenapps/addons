# -*- coding: utf-8 -*-
{
    'name': 'Slack Notifications',
    'version': '20.0.1.0.0',
    'summary': 'Notifications Slack sur événements Odoo (commandes, factures, stocks) via canaux configurés.',
    'description': '''Slack Notifications
===================
Notifications Slack sur événements Odoo (commandes, factures, stocks) via canaux configurés.

Business events in Odoo are not pushed to Slack channels.

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
    'category': 'Productivity/Discuss',
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
        'views/slack_connection_0_views.xml',
        'views/slack_record_1_views.xml',
        'views/slack_log_2_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
