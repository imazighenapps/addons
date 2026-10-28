# -*- coding: utf-8 -*-
{
    'name': 'PriceGuard - Purchase Price Compliance',
    'version': '18.0.1.0.0',
    'summary': 'Control supplier price agreements and flag vendor bills whose price exceeds the agreed price or tolerance.',
    'description': '''PriceGuard - Purchase Price Compliance
======================================
The invoice does not match the negotiated price. Again.

PriceGuard stores the unit price you agreed with each supplier, for each
product, with a validity period, a minimum quantity and a tolerance. It then
scans your posted vendor bills and compares every line with the agreement in
force. A small difference is accepted, a larger one raises a warning, and a
real overprice is flagged as a breach. Every check is recorded, can be ignored
with a documented decision, and is never created twice.

* One price agreement per supplier, product and validity period.
* Minimum quantity and configurable tolerance percentage.
* Automatic scan of posted vendor bills and refunds.
* Three levels: compliant, warning and breach.
* Idempotent scan: no duplicate check on a bill line.
* Ignore a check, then recalculate it if needed.
* Grouped views per supplier, product and status.
* Multi-company and multi-currency ready.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'category': 'Purchase/Purchase',
    'license': 'OPL-1',
    'price': 69.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
        'purchase',
        'account',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/price_agreement_0_views.xml',
        'views/price_check_1_views.xml',
        'views/menus.xml',
        'data/price_scan.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
