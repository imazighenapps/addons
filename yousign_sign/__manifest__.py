# -*- coding: utf-8 -*-
{
    'name': 'Yousign e-Signature',
    'version': '18.0.1.0.0',
    'summary': 'Create Yousign signature requests from documents, track signer status and store signed proofs in Odoo.',
    'description': '''Yousign e-Signature - Send and track signatures with Yousign
============================================================
Contracts, quotes and agreements often need electronic signatures. Without
integration, teams send documents manually and lose visibility on who
signed and when.

Yousign e-Signature manages connection settings, signature requests and
signers. Each request tracks its lifecycle (draft, sent, signed, declined,
expired) with timestamps and archived proof references, linked to business
documents and partners.

* Yousign connection profile with API key reference.
* Signature requests linked to documents/partners.
* Multiple signers with email and status.
* Lifecycle actions: prepare, send, mark signed/declined/expired, cancel.
* Proof/reference storage and event log.
* No external Python dependency.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Sales/Sign',
    'license': 'OPL-1',
    'price': 99.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
        'sale',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'data/sequence.xml',
        'views/yousign_connection_0_views.xml',
        'views/yousign_request_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
