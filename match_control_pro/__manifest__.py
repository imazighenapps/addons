# -*- coding: utf-8 -*-
{
    'name': 'MatchControlPro',
    'version': '20.0.1.0.0',
    'summary': 'Compare purchase orders, receipts and vendor bills line by line, flag quantity and price variances outside tolerance, and force a written reason before validating an exception.',
    'description': '''MatchControlPro - Three-Way Match for Purchase Orders, Receipts and Vendor Bills
==============================================================================
Pay only for what you ordered, received and were invoiced.

In most companies the vendor bill is approved by whoever happens to open the
mailbox, long after the goods were received. A supplier ships ten units
instead of twelve, bills twelve, and the difference is only discovered at the
annual audit. Three-way match closes that gap by comparing, line by line, the
quantities and unit prices of the purchase order, the receipt and the vendor
bill.

Create a check for a vendor bill, pick the purchase order and the receipt,
then run the match. MatchControlPro aggregates the ordered quantities from the
purchase order lines, the received quantities from the done stock moves of the
receipt, and the billed quantities from the invoice lines. Each line is marked
as compliant, quantity variance or price variance, and the check becomes an
exception as soon as one line falls outside the tolerance. A controller can
then validate a clean check, or flag an exception with a mandatory written
reason that stays in the audit trail. Validated checks are frozen, and the
whole history of runs, reasons and decisions is kept in the chatter.

* One check per vendor bill, enforced by a uniqueness rule per company.
* Ordered, received and billed quantities side by side on every line.
* Ordered and billed unit prices compared with a configurable tolerance.
* Line status: compliant, quantity variance or price variance.
* Automatic exception state as soon as one line is out of tolerance.
* Mandatory exception reason before a variance can be validated.
* Totals and variance amount recomputed from the lines.
* Draft, matched, exception and validated states with a full audit trail.
* Multi-company ready, no Enterprise dependency.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Accounting/Accounting',
    'license': 'OPL-1',
    'price': 99.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
        'purchase',
        'account',
    ],
    'data': [
        'security/security.xml',
        'security/ir.access.csv',
        'data/sequence.xml',
        'views/match_check_0_views.xml',
        'views/match_check_line_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
