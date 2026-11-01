# -*- coding: utf-8 -*-
{
    'name': 'BankImportPro',
    'version': '19.0.1.0.0',
    'summary': 'Parse CSV and CAMT bank statement files into statement lines, assign partners and accounts with matching rules, and flag transactions already imported.',
    'description': '''BankImportPro - Bank Statement Parsing, Rules and Duplicate Detection
=====================================================================
Importing a bank statement should not mean retyping it. Every month the
accounting team downloads CSV exports or CAMT files from the banks and
recreates the counterpart entries by hand: same labels, same amounts,
line after line. Between copy-paste fatigue and the labels that differ
from one bank to another, a transaction gets entered twice, a supplier
is never linked or a fee ends up in the wrong account, and the
reconciliation takes days instead of hours.

BankImportPro takes the file as it arrives. A batch stores the raw
content, its journal and its statement date, and one click turns the
file into statement lines with dates, labels, references and signed
amounts, separated by semicolons or CAMT-style entries. Matching rules
classify the recurring flows automatically: a label containing a
recognised pattern gets the right partner and the right account
immediately. Duplicate detection compares every new transaction with
what was already imported, so a statement processed twice is caught
before it creates a double entry. When the content cannot be parsed,
the batch itself reports the problem instead of crashing, and you can
fix the file and try again. Everything stays inside Accounting, with
no external dependency and no Enterprise module.

* CSV "date;label;reference;amount" parsing, one transaction per row.
* Minimal CAMT-style XML parsing with CRDT/DBIT indicators.
* Matching rules assign a partner and an account by label pattern.
* Idempotent rules: matched lines keep their assignment on re-run.
* Duplicate detection on date, amount and label of imported batches.
* Live batch total and per-line flags for a quick review.
* Invalid content sets an error state with a translated message.
* Chatter audit trail, multi-company, no Enterprise dependency.''',
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
        'views/bankimp_batch_0_views.xml',
        'views/bankimp_line_1_views.xml',
        'views/bankimp_rule_2_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
