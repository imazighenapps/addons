# -*- coding: utf-8 -*-
{
    'name': 'Pennylane Bridge',
    'version': '19.0.1.0.0',
    'summary': 'Export invoices, bills and payments from Odoo to Pennylane, track sync status and keep your accountant aligned.',
    'description': '''Pennylane Bridge - Sync your accounting with Pennylane
======================================================
Finance teams using Odoo for operations and Pennylane for accounting
collaboration often re-enter invoices and payments by hand. Entries drift,
documents get lost and month-end closing turns into reconciliation work.

Pennylane Bridge centralizes the connection settings and prepares accounting
documents for export: customer invoices, vendor bills and payments are queued
with their payload, mapped accounts and attachments references. Each export
is tracked with status, response message and retry information so nothing is
sent twice silently. A sync log keeps a full audit trail for the finance
team and the external accountant.

* Connection profile with company, environment and API token placeholder.
* Export queue for invoices, bills and payments with mapping details.
* Sync runs with status tracking (draft, ready, sent, error).
* Document payload snapshot and accountant-facing notes.
* Retry/reset actions and traceable error messages.
* Sync log history in the chatter and list views.
* Multi-company aware, no external Python dependency.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Accounting/Accounting',
    'license': 'OPL-1',
    'price': 129.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
        'account',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'data/sequence.xml',
        'views/pennylane_connection_0_views.xml',
        'views/pennylane_export_1_views.xml',
        'views/pennylane_sync_log_2_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
