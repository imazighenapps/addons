# -*- coding: utf-8 -*-
{
    'name': 'Pipedrive Bridge',
    'version': '18.0.1.0.0',
    'summary': 'Synchronize contacts and deals between Odoo CRM and Pipedrive with status tracking and sync logs.',
    'description': '''Pipedrive Bridge - Sync deals and contacts with Pipedrive
=========================================================
Sales teams using Pipedrive for pipeline management need customer and deal
data aligned with Odoo. Pipedrive Bridge stores connection settings and
sync records for persons/organizations and deals, tracking direction,
status and external IDs.

* Pipedrive connection with API token reference.
* Sync records for contacts and deals linked to Odoo records.
* Push/pull direction and lifecycle states.
* Prepare/sync/reset actions and logs.
* No external Python dependency.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Sales/CRM',
    'license': 'OPL-1',
    'price': 99.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
        'crm',
        'contacts',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'data/sequence.xml',
        'views/pipedrive_connection_0_views.xml',
        'views/pipedrive_sync_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
