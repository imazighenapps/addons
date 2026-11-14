# -*- coding: utf-8 -*-
{
    'name': 'FEC Export Pro',
    'version': '20.0.1.0.0',
    'summary': 'Exports FEC paramétrables, contrôles d’intégrité et historisation des générations.',
    'description': '''FEC Export Pro
==============
Exports FEC paramétrables, contrôles d’intégrité et historisation des générations.

FEC exports lack integrity checks and generation history in Odoo.

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
    'category': 'Accounting/Accounting',
    'license': 'OPL-1',
    'price': 99.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
        'account',
    ],
    'data': [
        'security/security.xml',
        'security/ir.access.csv',
        'views/fec_export_pro_connection_0_views.xml',
        'views/fec_export_pro_record_1_views.xml',
        'views/fec_export_pro_log_2_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
