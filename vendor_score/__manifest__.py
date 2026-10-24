# -*- coding: utf-8 -*-
{
    'name': 'VendorScore - Objective Supplier Rating',
    'version': '20.0.1.0.0',
    'summary': 'Score every supplier automatically on on-time delivery, fill rate, price variance and quality, then drive a documented improvement plan.',
    'description': '''VendorScore - Objective Supplier Rating
=======================================
Negotiate with facts, not with impressions.

VendorScore computes a supplier score from your real Odoo data: on-time
delivery, quantity received, price variance against the standard cost, and
the quality rate you record. Each review produces a score from 0 to 100, a
clear label, and an improvement plan with owners and deadlines.

* Automatic OTIF from purchase orders and receipts.
* Fill rate from received quantities.
* Price variance against the product standard cost.
* Manual quality rate from your non-conformities.
* Weighted score and A/B/C/D rating.
* Improvement plan with owner and deadline.
* Review history per supplier.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'category': 'Inventory/Purchase',
    'license': 'OPL-1',
    'price': 69.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
        'purchase',
        'stock',
    ],
    'data': [
        'security/security.xml',
        'security/ir.access.csv',
        'data/sequence.xml',
        'views/vendor_review_0_views.xml',
        'views/menus.xml',
        'views/partner_inherit.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
