# -*- coding: utf-8 -*-
{
    'name': 'AnomalyCheck',
    'version': '20.0.1.0.0',
    'summary': 'Scan bills before posting for impossible quantities, VAT mismatches and suspicious doublings of products.',
    'description': '''AnomalyCheck - Impossible Bills Caught
======================================
Supplier bills arrive fast and the obvious mistakes hide in plain sight:
a quantity multiplied by ten, a VAT amount that does not match the rate,
or the same product line quietly doubled on the same document. By the
time accounting spots the issue the payment run is already scheduled and
the correction becomes a trace of emails instead of a clean control.

AnomalyCheck gives finance a simple register of anomaly rules and a
queue of flagged checks to review before posting. Each rule describes
the control to apply, the tolerance to accept and the severity to raise
when a value crosses the line. Every check records the document
reference, the supplier name, the amounts under review and the reason it
was caught, so reviewers can confirm, resolve or reject the alert with a
clear note.

The result is a short, auditable trail of what was scanned, what looked
impossible and what was accepted with intent, without changing the
accounting entries themselves.

* A catalog of anomaly rules with control type, tolerance and severity.
* A queue of flagged checks with document reference and supplier.
* Quantity, tax and total amounts captured on every flagged check.
* Stored counters per rule to see how often each control fires.
* A review workflow to confirm, resolve or reject each finding.
* Search filters to focus on open, confirmed or resolved checks.
* Multi-company isolation for every rule and every check.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Accounting/Accounting',
    'license': 'OPL-1',
    'price': 49.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.access.csv',
        'views/anomaly_rule_0_views.xml',
        'views/anomaly_flag_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
