# -*- coding: utf-8 -*-
{
    'name': 'GDPR Request Desk',
    'version': '20.0.1.0.0',
    'summary': 'Suivi des demandes RGPD (accès, rectification, effacement) avec SLA et traçabilité.',
    'description': '''GDPR Request Desk
=================
Suivi des demandes RGPD (accès, rectification, effacement) avec SLA et traçabilité.

GDPR data subject requests are handled without traceable workflows.

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
    'category': 'Operations/Operations',
    'license': 'OPL-1',
    'price': 99.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.access.csv',
        'views/gdpr_request_connection_0_views.xml',
        'views/gdpr_request_record_1_views.xml',
        'views/gdpr_request_log_2_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
