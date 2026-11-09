# -*- coding: utf-8 -*-
{
    'name': 'TermAudit',
    'version': '19.0.1.0.0',
    'summary': 'Compare the payment terms stored on each customer with the due dates actually written on the invoices, and list every gap before it costs a late payment.',
    'description': '''TermAudit - Payment Terms That Match
====================================
The customer signed a contract with thirty-day terms. Somebody sold with a
sixty-day default, a copy-pasted partner forgot its payment term, and six
months later accountants chase the difference: the due date on the invoice
never matched the promise, and nobody noticed because the two numbers live
on two different records.

TermAudit reads them both. For a chosen period, every posted customer
invoice is compared with the payment term stored on its partner. The gap in
days is recorded, with the invoice, the partner, the expected and the actual
date, and the audit keeps one dated report per run. Terms that are missing
are anomalies on their own, so a partner sold on faith is not silently
accepted any more.

* One dated audit per period, replayable without duplicates.
* Expected days read from the partner payment term.
* Actual days read from the invoice itself.
* Gap flagged beyond a configurable tolerance.
* Missing terms reported as their own anomaly kind.
* Lines can be ignored when a gap is a real agreement.
* Company isolation, filters by kind and partner.
* Draft and done states, one click to re-run.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Accounting/Accounting',
    'license': 'OPL-1',
    'price': 79.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'account',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'views/payment_term_audit_0_views.xml',
        'views/payment_term_audit_line_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
