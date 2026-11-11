# -*- coding: utf-8 -*-
{
    'name': 'AuditBinder',
    'version': '18.0.1.0.0',
    'summary': 'Assemble the audit evidence pack per account and period: entries, documents and reconciliations in one bind.',
    'description': '''AuditBinder - The Binder Before They Ask
========================================
An audit request always arrives the same way: a list of accounts and a
period, with a week to produce the supporting evidence. The entries live
in the ledger, the documents live in mailboxes and shared drives, and the
reconciliations live in someone else's spreadsheet. Building the pack is
a scramble that repeats every year.

AuditBinder keeps one binder per period in Odoo. Each binder is split
into sections for the accounts or topics the auditor will review, and
every section holds the evidence items you attach to it with a reference
and a short description. A ready flag on each item and stored counters on
the binder show exactly what is still missing, and the binder can be
closed once every item is ready. The pack the auditor asks for is the
pack the module already assembled.

* One audit binder per period with a clear preparation status.
* Sections per account or topic inside each binder.
* Evidence items with a reference and a description per section.
* A ready flag on every item and missing counters on the binder.
* The binder closes only when every evidence item is ready.
* One screen listing every item still missing.
* Multi-company isolation out of the box.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Accounting/Accounting',
    'license': 'OPL-1',
    'price': 59.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'views/audit_binder_0_views.xml',
        'views/audit_binder_item_1_views.xml',
        'views/audit_missing_2_views.xml',
        'views/menus.xml',
        'views/audit_missing_action.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
