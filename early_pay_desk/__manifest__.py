# -*- coding: utf-8 -*-
{
    'name': 'EarlyPay',
    'version': '18.0.1.0.0',
    'summary': 'Grab every early payment discount vendors offer: the due window, the gain per booking and what you let slip.',
    'description': '''EarlyPay - Discounts Never Missed
=================================
Suppliers offer early payment discounts in the small print: two percent if you
pay within ten days, nothing if you miss the window by a morning. The offer
sits in a PDF, the due date in the inbox and the gain nobody measured ends up
as money quietly left on the table at month end.

EarlyPay records each discount offer against the vendor bill or reference, with
the gross amount, the discount rate, the discount deadline and the normal due
date. The discount amount and the net amount to pay are computed and stored as
soon as the offer is entered, so the saving is visible before the payment is
booked. Captured and missed offers are marked with the outcome, and the list of
offers still open shows which discounts must be taken before their window
closes. Nothing is calculated twice and nothing is forgotten.

* A register of vendor early payment discount offers.
* Gross amount, discount rate and stored discount amount per offer.
* Discount deadline and normal due date on every offer.
* Stored net amount to pay when the discount is captured.
* Open, captured and missed states with a dated decision.
* One screen for offers whose discount window is still open.
* Impossible dates and rates refused before they are saved.
* Multi-company isolation out of the box.''',
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
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'views/earlypay_offer_0_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
