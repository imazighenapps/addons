# -*- coding: utf-8 -*-
{
    'name': 'HubSpot Bridge',
    'version': '18.0.1.0.0',
    'summary': 'Synchronize contacts and deals between Odoo CRM and HubSpot with mapping, sync logs and status tracking.',
    'description': '''HubSpot Bridge - Sync CRM data with HubSpot
===========================================
When marketing runs on HubSpot and sales/operations on Odoo, contacts and
deals diverge. HubSpot Bridge provides connection settings, object mappings
and sync records for contacts and deals so teams can track what was synced
and resolve errors.

* HubSpot connection with token reference and pipeline defaults.
* Sync records for contacts (partners) and deals (opportunities).
* Direction and status tracking (draft, ready, synced, error).
* External IDs, payload snapshots and error messages.
* Sync logs and manual actions.
* No external Python dependency.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Sales/CRM',
    'license': 'OPL-1',
    'price': 129.0,
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
        'views/hubspot_connection_0_views.xml',
        'views/hubspot_sync_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
