# -*- coding: utf-8 -*-
{
    'name': 'Xero Bridge',
    'version': '20.0.1.0.0',
    'summary': 'Pont comptable Xero : contacts, factures, paiements et rapprochements journalisés.',
    'description': '''Xero Bridge
===========
Pont comptable Xero : contacts, factures, paiements et rapprochements journalisés.

Xero and Odoo accounting records diverge without a tracked synchronization.

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
    'price': 149.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
        'account',
    ],
    'data': [
        'security/security.xml',
        'security/ir.access.csv',
        'views/xero_connection_0_views.xml',
        'views/xero_record_1_views.xml',
        'views/xero_log_2_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
