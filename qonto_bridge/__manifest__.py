# -*- coding: utf-8 -*-
{
    'name': 'Qonto Bridge',
    'version': '18.0.1.0.0',
    'summary': 'Import Qonto transactions, match them to payments and expenses, and track synchronization status from Odoo.',
    'description': '''Qonto Bridge - Bank transactions and expenses in sync
=====================================================
SMEs using Qonto need bank transactions and card expenses reflected in
Odoo for reconciliation and expense tracking. Manual exports slow down
accounting and increase matching errors.

Qonto Bridge stores connection credentials references, imports transaction
records, and lets accountants match them to payments or expenses. Each
transaction carries amount, counterpart, status and attachment references,
with sync logs and reconciliation states for a clear audit trail.

* Qonto connection profile (organization, IBAN, token reference).
* Transaction import records with category and counterparty.
* Matching states: new, matched, ignored.
* Link to journal/payment or expense reference fields.
* Sync runs and status logs.
* Attachment/note tracking per transaction.
* No external Python dependency.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Accounting/Accounting',
    'license': 'OPL-1',
    'price': 119.0,
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
        'views/qonto_connection_0_views.xml',
        'views/qonto_transaction_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
