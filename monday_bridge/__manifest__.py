# -*- coding: utf-8 -*-
{
    'name': 'Monday.com Bridge',
    'version': '19.0.1.0.0',
    'summary': 'Synchronisation tableaux/items Monday.com avec projets/tâches Odoo.',
    'description': '''Monday.com Bridge
=================
Synchronisation tableaux/items Monday.com avec projets/tâches Odoo.

Monday.com work tracking is disconnected from Odoo projects.

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
    'price': 129.0,
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
        'views/monday_connection_0_views.xml',
        'views/monday_record_1_views.xml',
        'views/monday_log_2_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
